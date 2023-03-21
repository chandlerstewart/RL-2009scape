package python;

import com.google.gson.Gson;
import rs09.game.ai.AIPlayer;


import java.util.ArrayList;

public class PyBotManager {

    public static ArrayList<AIPlayer> botList = new ArrayList<AIPlayer>();

    public static String getJSONBotStatus(){

        ArrayList<BotInfo> botInfoList = new ArrayList<BotInfo>();

        for (AIPlayer bot : botList){
            String name = bot.getName();
            int xLoc = bot.getLocation().getX();
            int yLoc = bot.getLocation().getY();

            botInfoList.add(new BotInfo(name,xLoc,yLoc));
        }

        Gson gson = new Gson();
        String json = gson.toJson(botInfoList);
        return json;
    }


    public static void takeActions(ArrayList<BotInfo> botInfoList) {

        for(int i=0; i<botInfoList.size(); i++){
            AIPlayer bot = botList.get(i);
            int xLoc = botInfoList.get(i).xLoc;
            int yLoc = botInfoList.get(i).yLoc;

            bot.walkToPosSmart(xLoc,yLoc);
        }
    }

    public static void removeBots(){
        for (AIPlayer aiPlayer : botList){
            aiPlayer.clear();
        }

        botList.clear();
    }
}


class BotInfo {

    String name;
    int xLoc;
    int yLoc;
    BotInfo(String name, int xLoc, int yLoc){
        this.name = name;
        this.xLoc = xLoc;
        this.yLoc = yLoc;
    }
}
