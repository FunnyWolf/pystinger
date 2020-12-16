<%@ page language="java" import="java.net.*,java.util.*,java.io.*,java.net.*" contentType="text/html; charset=utf-8" %>
<%!
    public static class HttpRequest {
		public static String doPost(String httpUrl, byte[] param) {
			StringBuffer result=new StringBuffer();
			HttpURLConnection connection=null;
			OutputStream os=null;
			InputStream is=null;
			BufferedReader br=null;
			try {
				URL url=new URL(httpUrl);
				connection= (HttpURLConnection) url.openConnection();
				connection.setRequestMethod("POST");
				connection.setConnectTimeout(10000);
				connection.setReadTimeout(10000);
				connection.setDoOutput(true);
				connection.setDoInput(true);
				connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
				//connection.setRequestProperty("accept", "*/*");
				//connection.setRequestProperty("Connection", "keep-alive");
				if(param!=null&&!param.equals("")){
					os=connection.getOutputStream();
					os.write(param);
				}
				if(connection.getResponseCode()==200){
					is=connection.getInputStream();
					if(is!=null){
						br=new BufferedReader(new InputStreamReader(is,"UTF-8"));
						String temp=null;
						if((temp=br.readLine())!=null){
							result.append(temp);
						}
					}
				}
			}  catch (Exception e) {
                System.out.println("error to send post" + e);
                return e.toString();
            }  finally {
				if(br!=null){
					try {
						br.close();
					} catch (IOException e) {
						e.printStackTrace();
					}
				}
				if(os!=null){
					try {
						os.close();
					} catch (IOException e) {
						e.printStackTrace();
					}
				}
				if(is!=null){
					try {
						is.close();
					} catch (IOException e) {
						e.printStackTrace();
					}
				}
				//关闭连接
				connection.disconnect();
			}
			return result.toString();
		}
    }
%>
<%
    String method = request.getMethod();
    if (method.equals("GET")) {
        out.print("UTF-8");
        return;
    } else if (method.equals("POST")) {
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
        returnString = HttpRequest.doPost(url, post_arg.getBytes());
        out.print(returnString);
    }
%>
