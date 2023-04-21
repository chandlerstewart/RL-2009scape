package python;

//import rt4.*;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import core.game.container.impl.EquipmentContainer;
import core.game.node.entity.player.Player;
import core.game.node.entity.skill.Skills;
import core.game.node.item.Item;
import core.game.world.map.Location;
import core.game.world.map.path.Pathfinder;
import org.rs09.consts.Items;
import rs09.game.ai.AIPlayer;
import rs09.game.world.repository.Repository;

import java.lang.reflect.Type;
import java.util.*;

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
                GenerateBot(new Location(x, y), numOfBots, message.getInfo());
                String jsonBotStatus = PyBotManager.getJSONBotStatus(null);

                return new Message("Success: spawn_bots", String.valueOf(jsonBotStatus.length()*2));
            case "server_waiting":
                return new Message("json", PyBotManager.getJSONBotStatus(null));
            case "json":
                Type listType = new TypeToken<ArrayList<HashMap<String, Object>>>(){}.getType();
                ArrayList<HashMap<String, Object>> listOfMaps = new Gson().fromJson(message.getInfo(), listType);
                ArrayList<BotInfo> botInfoList = BotInfo.mapToBotInfo(listOfMaps);
                ArrayList <Integer> rewards = PyBotManager.takeActions(botInfoList);
                return new Message("json", PyBotManager.getJSONBotStatus(rewards));

            default:
                System.out.println("DEFAULT");
                return new Message("", "");

        }
    }

    private static void GenerateBot(Location location, int numOfBots, String activity){

        if (PyBotManager.botList.size() > 0){
            PyBotManager.removeBots();
        }


        for (int i=0; i<numOfBots; i++){
            AIPlayer aiPlayer = new AIPlayer("Bot" + i, location, "");

            PyBotManager.botList.add(aiPlayer);

            if (activity.equals("woodcutting")){
                Item rune_axe = new Item(Items.RUNE_AXE_1359);
                aiPlayer.equipIfExists(rune_axe, EquipmentContainer.SLOT_WEAPON);
                aiPlayer.getSkills().setStaticLevel(Skills.WOODCUTTING, 99);
                aiPlayer.getSkills().setStaticLevel(Skills.ATTACK, 50);
                aiPlayer.getSkills().setStaticLevel(Skills.STRENGTH, 50);
            }
        }
    }

    }

