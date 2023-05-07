package python;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import core.game.node.Node;
import core.game.world.map.Direction;
import core.game.world.map.Location;
import core.game.world.map.RegionManager;
import org.json.simple.JSONObject;
import rs09.game.ai.AIPlayer;


import java.util.ArrayList;
import java.util.HashMap;

public class PyBotManager {

    public static ArrayList<AIPlayer> botList = new ArrayList<AIPlayer>();
    public static Integer nodeRange = 0;

    public static String getJSONBotStatus(ArrayList rewards){

        ArrayList<JsonElement> botInfoList = new ArrayList<JsonElement>();


        for (int i=0;i<botList.size();i++){
            AIPlayer bot = botList.get(i);
            String name = bot.getName();
            int xLoc = bot.getLocation().getX();
            int yLoc = bot.getLocation().getY();
            boolean canMoveNorth = bot.canMove(Location.create(xLoc,yLoc+1), Direction.NORTH);
            boolean canMoveSouth = bot.canMove(Location.create(xLoc,yLoc-1), Direction.SOUTH);
            boolean canMoveEast = bot.canMove(Location.create(xLoc+1,yLoc), Direction.EAST);
            boolean canMoveWest = bot.canMove(Location.create(xLoc-1,yLoc), Direction.WEST);

            BotInfo botInfo = new BotInfo();
            botInfo.put("xLoc", xLoc);
            botInfo.put("yLoc", yLoc);
            botInfo.put("name", name);
            botInfo.put("canMoveNorth", canMoveNorth);
            botInfo.put("canMoveSouth", canMoveSouth);
            botInfo.put("canMoveEast", canMoveEast);
            botInfo.put("canMoveWest", canMoveWest);

            botInfo.put("freeInvSpace", bot.getInventory().freeSlots());

            if (rewards == null){
                botInfo.put("reward",0);
            } else {
                botInfo.put("reward", rewards.get(i));
            }

            //addNearbyNodesToBotInfo(bot, botInfo);
            botInfo.put("nearbyNodes",bot.getNodesInRange(nodeRange));

            botInfoList.add(botInfo.toJsonElement());
        }

        Gson gson = new Gson();
        String jsonString = gson.toJson(botInfoList);
        return jsonString;
    }

    private static void addNearbyNodesToBotInfo(AIPlayer aiplayer, BotInfo botInfo){
        int x = aiplayer.getLocation().getX();
        int y = aiplayer.getLocation().getY();

        Node northNode = RegionManager.getObject(0, x, y+1);
        Node southNode = RegionManager.getObject(0, x, y-1);
        Node eastNode = RegionManager.getObject(0, x+1, y);
        Node westNode = RegionManager.getObject(0, x-1, y);

        addNodeHelper(northNode, "northNode", botInfo);
        addNodeHelper(southNode, "southNode", botInfo);
        addNodeHelper(eastNode, "eastNode", botInfo);
        addNodeHelper(westNode, "westNode", botInfo);


    }

    private static void addNodeHelper(Node node, String nodeName, BotInfo botInfo){
        if (node != null){
            botInfo.put(nodeName,true);
        } else {
            botInfo.put(nodeName,false);
        }
    }




    public static ArrayList<Integer> takeActions(ArrayList<BotInfo> botInfoList) {

        ArrayList <Integer> rewardList = new ArrayList<>();

        for(int i=0; i<botInfoList.size(); i++){

            rewardList.add(0);
            AIPlayer bot = botList.get(i);
            HashMap botMap = botInfoList.get(i).map;

            int xLoc = ((Double) botMap.get("xLoc")).intValue();
            int yLoc = ((Double) botMap.get("yLoc")).intValue();

            if (botMap.get("interact").equals("none")) {
                bot.walkToPosSmart(xLoc, yLoc);
            } else {
                Node node = null;
                if (botMap.get("interact").equals("north")){
                    node = RegionManager.getObject(0, xLoc, yLoc+1);
                }
                if (botMap.get("interact").equals("south")){
                    node = RegionManager.getObject(0, xLoc, yLoc-1);
                }
                if (botMap.get("interact").equals("east")){
                    node = RegionManager.getObject(0, xLoc+1, yLoc);
                }
                if (botMap.get("interact").equals("west")){
                    node = RegionManager.getObject(0, xLoc-1, yLoc);
                }

                if (node != null){

                    switch(node.getName()){
                        case "Tree":
                        case "Maple Tree":
                        case "Oak Tree":
                            if (bot.getInventory().freeSlots() > 0){
                                bot.chop(node);
                                //rewardList.add(i, 1);
                                rewardList.add(i, bot.getInventory().capacity() - bot.getInventory().freeSlots());
                            }
                            break;
                        case "Bank booth":
                            rewardList.add(i, (bot.getInventory().capacity() - bot.getInventory().freeSlots()) * 1000);
                            bot.getInventory().clear();

                    }


                }
            }
        }


        return rewardList;
    }

    public static void removeBots(){
        for (AIPlayer aiPlayer : botList){
            aiPlayer.clear();
        }

        botList.clear();
    }

    private static int boolToInt(boolean boolVal){
        return boolVal? 1 : 0;
    }
}


class BotInfo {

    public HashMap<String, Object> map;

    BotInfo(){
        map = new HashMap<>();
    }

    BotInfo(HashMap map){
        this.map = map;
    }

    public void put(String key, Object value){
        map.put(key,value);
    }

    public JsonElement toJsonElement(){
        Gson gson = new Gson();
        JsonElement jsonElement = gson.toJsonTree(map);
        return jsonElement;
    }

    public String toJsonString(){
        Gson gson = new Gson();
        JsonElement jsonElement = toJsonElement();
        JsonObject jsonObject = jsonElement.getAsJsonObject();
        String jsonString = gson.toJson(jsonObject);
        return jsonString;
    }

    public static ArrayList<BotInfo> mapToBotInfo(ArrayList<HashMap<String, Object>> listOfMaps){
        ArrayList<BotInfo> botInfoList = new ArrayList<>();
        for (HashMap map : listOfMaps){
            botInfoList.add(new BotInfo(map));
        }

        return botInfoList;
    }
}
