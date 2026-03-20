<?php

require '/var/www/html/wp-load.php';

global $wpdb;

$consumer_key = 'ck_' . wc_rand_hash();
$consumer_secret = 'cs_' . wc_rand_hash();

$wpdb->insert(
    $wpdb->prefix . 'woocommerce_api_keys',
    array(
        'user_id' => 1,
        'description' => 'Codex Local API',
        'permissions' => 'read_write',
        'consumer_key' => wc_api_hash($consumer_key),
        'consumer_secret' => $consumer_secret,
        'truncated_key' => substr($consumer_key, -7),
    )
);

echo json_encode(
    array(
        'consumer_key' => $consumer_key,
        'consumer_secret' => $consumer_secret,
    ),
    JSON_UNESCAPED_SLASHES
);
