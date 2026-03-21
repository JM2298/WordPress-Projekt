<?php
/**
 * Plugin Name: Local HTTP Host Allowlist
 * Description: Allows WordPress HTTP API to fetch local Docker-hosted images.
 */

add_filter(
    'http_request_host_is_external',
    static function ($allow, $host, $url) {
        $allowed_hosts = array(
            'host.docker.internal',
            'nginx',
            'backend_django_dev',
            'localhost',
        );

        if (in_array((string) $host, $allowed_hosts, true)) {
            return true;
        }

        return $allow;
    },
    10,
    3
);
