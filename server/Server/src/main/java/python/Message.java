package python;

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

    public String getInfo() {
        return info;
    }
}