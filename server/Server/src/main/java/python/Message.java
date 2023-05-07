package python;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.HashMap;

class Message {
    private String command;
    private String info;

    public Message(String command, String info) {
        this.command = command;
        this.info = info;
    }


    public void setCommand(String command) {
        this.command = command;
    }

    public void setInfo(String info) {
        this.info = info;
    }

    public String getCommand() {
        return command;
    }

    public ArrayList<BotInfo> getInfo() {
        Type listType = new TypeToken<ArrayList<HashMap<String, Object>>>(){}.getType();
        ArrayList<HashMap<String, Object>> listOfMaps = new Gson().fromJson(info, listType);
        ArrayList<BotInfo> botInfoList = BotInfo.mapToBotInfo(listOfMaps);
        return botInfoList;
    }
}