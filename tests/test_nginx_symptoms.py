"""Match sanitized nginx messages through the public knowledge-base API.

Message text verified against nginx's source and public error logs:
https://github.com/nginx/nginx/blob/master/src/core/ngx_connection.c
https://github.com/nginx/nginx/blob/master/src/http/ngx_http_core_module.c
https://github.com/nginx/nginx/blob/master/src/http/ngx_http_upstream.c
https://github.com/nginx/nginx/blob/master/src/event/ngx_event_connect.c
https://github.com/nginx/nginx/blob/master/src/os/win32/ngx_errno.h
https://trac.nginx.org/nginx/ticket/2026
https://trac.nginx.org/nginx/ticket/2103

Paths, addresses and process IDs are synthetic. OS error codes cover Linux,
macOS and Windows; these tests do not start nginx or change local services.
"""

import re

import pytest

from localhost_doctor import knowledge


@pytest.mark.parametrize(
    "message, symptom_id",
    [
        (
            'nginx: [emerg] bind() to 0.0.0.0:80 failed '
            '(98: Address already in use)',
            'nginx_port_in_use',
        ),
        (
            'nginx: [emerg] bind() to [::]:80 failed '
            '(48: Address already in use)',
            'nginx_port_in_use',
        ),
        (
            'nginx: [emerg] bind() to 0.0.0.0:80 failed '
            '(10048: Only one usage of each socket address '
            '(protocol/network address/port) is normally permitted)',
            'nginx_port_in_use',
        ),
        (
            '[error] 100#100: *1 directory index of "/srv/site/" is forbidden, '
            'client: 127.0.0.1, server: localhost, request: "GET / HTTP/1.1"',
            'nginx_directory_index_forbidden',
        ),
        (
            '[error] 100#100: *1 directory index of "C:/nginx/html/" is forbidden',
            'nginx_directory_index_forbidden',
        ),
        (
            '[error] 100#100: *1 connect() failed (111: Connection refused) '
            'while connecting to upstream, upstream: "http://127.0.0.1:3000/"',
            'nginx_upstream_connection_refused',
        ),
        (
            '[error] 100#100: *1 connect() to 127.0.0.1:9000 failed '
            '(111: Connection refused) while connecting to upstream, '
            'upstream: "fastcgi://127.0.0.1:9000"',
            'nginx_upstream_connection_refused',
        ),
        (
            '[error] 100#100: *1 connect() failed (61: Connection refused) '
            'while connecting to upstream, upstream: "http://127.0.0.1:3000/"',
            'nginx_upstream_connection_refused',
        ),
        (
            '[error] 100#100: *1 connect() failed (10061: No connection could '
            'be made because the target machine actively refused it) '
            'while connecting to upstream, upstream: "fastcgi://127.0.0.1:9000"',
            'nginx_upstream_connection_refused',
        ),
    ],
)
def test_nginx_error_messages(message, symptom_id):
    results = knowledge.explain(message)
    result = next(item for item in results if item['id'] == symptom_id)

    assert result['stack'] == 'nginx'
    assert result['matched']
    assert result['title']
    assert result['causes']
    assert result['fixes']


@pytest.mark.parametrize(
    'message',
    [
        'the weather is nice today',
        '403 Forbidden',
        '502 Bad Gateway',
        'nginx: [emerg] bind() to 0.0.0.0:80 failed (13: Permission denied)',
        'nginx: [emerg] bind() to 0.0.0.0:80 failed (10013: Access denied)',
        '[error] connect() failed (111: Connection refused) while connecting to database',
        '[error] connect() failed (13: Permission denied) while connecting to upstream',
        '[error] upstream timed out (110: Connection timed out) while reading response header from upstream',
        'AH00072: make_sock: could not bind to address 0.0.0.0:80',
    ],
)
def test_unrelated_errors_do_not_match_nginx(message):
    assert not any(item['stack'] == 'nginx' for item in knowledge.explain(message))


def test_existing_symptoms_still_match():
    assert any(
        item['id'] == 'apache_port_in_use'
        for item in knowledge.explain(
            '(10048) Only one usage of each socket address : AH00072: '
            'make_sock: could not bind to address 0.0.0.0:80'
        )
    )
    assert any(
        item['id'] == 'mysql_shutdown_unexpectedly'
        for item in knowledge.explain('MySQL shutdown unexpectedly')
    )


def test_all_knowledge_base_patterns_compile():
    for entry in knowledge.load_entries():
        for pattern in entry['match']:
            re.compile(pattern, re.IGNORECASE)
