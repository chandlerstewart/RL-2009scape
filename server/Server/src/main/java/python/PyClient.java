package python;
import java.io.*;
import java.net.*;
import com.google.gson.Gson;

public class PyClient{

    private static String hostName = "localhost";
    private static int portNumber = 5000;
    private static Message message = new Message("Connected", "");


    public static void sendStatus(){

        try (
                Socket socket = new Socket(hostName, portNumber);
                DataOutputStream out = new DataOutputStream(socket.getOutputStream());
                BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        ) {
            Gson gson = new Gson();

            // Send message to server
            String jsonMessage = gson.toJson(message);
            out.writeUTF(jsonMessage);

            // Receive response from server
            String jsonResponse = in.readLine();
            Message response = gson.fromJson(jsonResponse, Message.class);

            out.close();
            socket.close();

            if (response != null) {
                System.out.println("Server response: " + response.getCommand());
                message = PyCommands.ProcessCommand(response);
            }
        } catch (IOException e) {
            System.err.println("Couldn't get I/O for the connection to " +
                    hostName);
            resetMessage();
        }
    }

    private static void resetMessage(){
        message = new Message("Connected", "");
    }

}


