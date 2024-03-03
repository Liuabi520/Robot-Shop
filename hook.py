import frida
import sys
import json 

# JavaScript code to be injected

hash_table = {}

js_script = """

Interceptor.attach(Module.findExportByName(null, 'connect'), {
    onEnter: function(args) {
        // `args[1]` points to the `sockaddr` structure
        console.log("connect called - FD: " + args[0].toInt32());
        var family = Memory.readU16(args[1]);
        // AF_INET (IPv4) family is usually 2 on most systems
        if (family === 2) {
            var ip = [args[1].add(4).readU8(), 
                      args[1].add(5).readU8(), 
                      args[1].add(6).readU8(), 
                      args[1].add(7).readU8()].join('.');
            var port = args[1].add(2).readU16();
            console.log('IP: ' + ip + 'port: ' + port);
            send('Connect|IP: ' + ip + 'port: ' + port + ' FD: ' + args[0].toInt32());
        }
    }
});
Interceptor.attach(Module.findExportByName(null, 'write'), {
    onEnter: function(args) {
        // `args[1]` points to the `sockaddr` structure
        console.log("write called - FD: " + args[0].toInt32());
        var data = Memory.readUtf8String(args[1], args[2].toInt32());
        console.log('Data: ' + data);
        send('Write|FD: ' + args[0].toInt32() + ' Data: ' + data);
        },
});

"""
def on_message(message, data):
    message = message['payload']
    # ip =message.split('IP: ')[1].split('port:')[0]
    # port = message.split('port: ')[1].split(' FD:')[0]
    # FD = message.split('FD: ')[1]
    # print(f"[*] IP: {ip} Port: {port} FD: {FD}")
    # with open('output.json', 'a') as f:
    #     json.dump({"IP": ip, "Port": port, "FD": FD}, f)
    #     f.write('\n')

    #   "requests": [
    # {
    #   "path": "/ratings/*",
    #   "method": "GET",
    #   "name": "ratings",
    #   "type": "http",
    #   "url": "http://ratings:9080/ratings/*"
    # },
    # {"22": {"IP Address": "10.102.104.96", "Port": "36895", 
    # "data": "GET /product/STAN-1 HTTP/1.1\r\nhost: catalogue:8080\r\nConnection: close\r\n\r\n"}}
    message = message.split('|')
    if message[0] == 'Connect':
        ip = message[1].split('IP: ')[1].split('port:')[0]
        port = message[1].split('port: ')[1].split(' FD:')[0]
        FD = message[1].split('FD: ')[1]
        print(f"[*] IP: {ip} Port: {port} FD: {FD}")
        hash_table[FD] = {"IP Address": ip,  "Port": port}
        hash_table[FD]["data"] = {}

    elif message[0] == 'Write':
        FD = message[1].split('FD: ')[1].split(' Data:')[0]
        data = message[1].split('Data: ')[1]
        if FD in hash_table:
            keywords = data.split("\r\n") 
            get_request = keywords[0]
            get_request = get_request.split(" ")
            method, path, _type = get_request[0], get_request[1], get_request[2]
            
            host = keywords[1]
            host_info = host.split(" ") 
            host_path = host_info[1] 
            name = host_path.split(":")[0]
            
            full_path = f"http://{host_path}{path}"
            hash_table[FD]["data"]["path"] = path 
            hash_table[FD]["data"]["method"] = method
            hash_table[FD]["data"]["name"] = name
            hash_table[FD]["data"]["type"] = _type
            hash_table[FD]["data"]["url"] = full_path

            with open('output.json', 'a') as f:
                json.dump(hash_table, f)
                f.write('\n')
            





def main(target_process):
    # Attach to the target Node.js process
    session = frida.attach(target_process)

    # Create a script with the JavaScript code
    script = session.create_script(js_script)

    # Listen for messages sent from the script
    script.on('message', on_message)

    # Load the script into the target process
    script.load()

    # Keep the script running
    input('[*] Press enter to exit...')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python hook.py <process_name_or_PID>")
        sys.exit(1)

    main(sys.argv[1])