package python;

//import rt4.*;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import core.game.node.entity.player.Player;
import core.game.world.map.Location;
import core.game.world.map.path.Pathfinder;
import rs09.game.ai.AIPlayer;
import rs09.game.world.repository.Repository;

import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

public class PyCommands {

    public static Message ProcessCommand(Message message){


        String command = message.getCommand();
        String[] split = message.getCommand().split(" ");

        System.out.println(command);


        switch(split[0]){
            case "spawn_bots":
                int x = Integer.valueOf(split[1]);
                int y = Integer.valueOf(split[2]);
                int numOfBots = Integer.valueOf(split[3]);
                GenerateBot(new Location(x, y), numOfBots);
                String jsonBotStatus = PyBotManager.getJSONBotStatus();
                return new Message("Success: spawn_bots", String.valueOf(jsonBotStatus.length()*2));
            case "server_waiting":
                return new Message("json", PyBotManager.getJSONBotStatus());
            case "json":
                Type listType = new TypeToken<ArrayList<BotInfo>>(){}.getType();
                ArrayList<BotInfo> botInfoList = new Gson().fromJson(message.getInfo(), listType);
                PyBotManager.takeActions(botInfoList);
                return new Message("json", PyBotManager.getJSONBotStatus());
            default:
                System.out.println("DEFAULT");
                return new Message("", "");

        }
    }

    private static void GenerateBot(Location location, int numOfBots){

        if (PyBotManager.botList.size() > 0){
            PyBotManager.removeBots();
        }


        for (int i=0; i<numOfBots; i++){
            AIPlayer aiPlayer = new AIPlayer("Bot" + i, location, "");

            PyBotManager.botList.add(aiPlayer);
        }
    }

    }

