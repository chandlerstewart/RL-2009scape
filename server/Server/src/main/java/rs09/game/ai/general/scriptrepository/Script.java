package rs09.game.ai.general.scriptrepository;

import core.game.node.entity.player.Player;
import rs09.game.ai.general.ScriptAPI;
import core.game.node.item.Item;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public abstract class Script {

    public ScriptAPI scriptAPI;
    public ArrayList<Item> inventory = new ArrayList<>(20);
    public ArrayList<Item> equipment = new ArrayList<>(20);
    public Map<Integer, Integer> skills = new HashMap<>();


    public Player bot;

    public boolean running = true;

    public void init(boolean isPlayer)
    {
        //bot.init();
        scriptAPI = new ScriptAPI(bot);

        if(!isPlayer) {
            for (Item i : equipment) {
                bot.getEquipment().add(i, true, false);
            }
            bot.getInventory().clear();
            for (Item i : inventory) {
                bot.getInventory().add(i);
            }
            for (Map.Entry<Integer, Integer> skill : skills.entrySet()) {
                setLevel(skill.getKey(), skill.getValue());
            }
        }
    }

    @Override
    public String toString() {
        return bot.getName() + " is a " + this.getClass().getSimpleName() + " at location " + bot.getLocation().toString() + " Current pulse: " + bot.getPulseManager().getCurrent();
    }

    public abstract void tick();

    public void setLevel(int skill, int level) {
        bot.getSkills().setLevel(skill, level);
        bot.getSkills().setStaticLevel(skill, level);
        bot.getSkills().updateCombatLevel();
        bot.getAppearance().sync();
    }

    // This does not get called and all implementations should be removed
    public abstract Script newInstance();
}