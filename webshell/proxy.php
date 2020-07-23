<?php
ini_set("display_errors", "On");
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    exit("UTF-8");
}
function my_socket_post($url, $data)
{
    $url = parse_url($url);
    if (empty ($url ['scheme']) || $url ['scheme'] != 'http') {
        die ("Error: Only HTTP request are supported !");
    }
    $host = $url ['host'];
    $port = $url ['port'];
    $path = isset ($url ['path']) ? $url ['path'] : '/';
    $fp = fsockopen($host, $port, $errno, $errstr, 3);
    if ($fp) {
        // send the request headers:
        $length = strlen($data);
        $POST = <<<HEADER
POST {$path} HTTP/1.1
Host: {$host}:$port
Accept: */*
Content-Length: {$length}
Content-Type: application/x-www-form-urlencoded\r\n
{$data}
HEADER;
        fwrite($fp, $POST);
        $result = '';
        $result .= fread($fp, 10240);
//        while (!feof($fp)) {
//            $result .= fread($fp, 4096);
//        }
    } else {
        return array(
            'status' => 'error',
            'error' => "$errstr ($errno)"
        );
    }
    // close the socket connection:
    fclose($fp);
    // split the result header from the content
    $result = explode("\r\n\r\n", $result, 2);
    print_r(isset ($result [1]) ? $result [1] : '');
}
function post($url, $data)
{

  //$postdata = http_build_query($data);
  $opts = array('http' =>
           array(
             'method' => 'POST',
             'header' => 'Content-type: application/x-www-form-urlencoded',
             'content' => $data
           )
  );
  $context = stream_context_create($opts);
  $result = file_get_contents($url, false, $context);
  print_r($result);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $post_arg = file_get_contents("php://input");
    $RemoteServer = $_POST['Remoteserver'];
    $Endpoint = $_POST['Endpoint'];
    if (function_exists('stream_context_create')) {
        $url = $RemoteServer . $Endpoint;
        post($url, $post_arg);
    }
    elseif (function_exists("curl_init")) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post_arg);
        curl_setopt($ch, CURLOPT_URL, $RemoteServer . $Endpoint);
        curl_exec($ch);
        curl_close($ch);
    } elseif (function_exists("fsockopen")) {
        $url = $RemoteServer . $Endpoint;
        my_socket_post($url, $post_arg);
    }else {
        exit("UTF-8 error!");
    }
}
?>