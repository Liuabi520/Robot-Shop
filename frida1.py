import frida
import sys
import time

# JavaScript code for Frida hook
js_script = """
const PROXY_IP = '127.0.0.1'; // Proxy IP address
var PROXY_PORT = 9998; // Proxy listening port
PROXY_PORT = ((PROXY_PORT & 0xFF) << 8) | ((PROXY_PORT >> 8) & 0xFF);
const newAddr = Memory.alloc(16); // Allocate memory for the structure
Memory.writeU16(newAddr, 2); // AF_INET
Memory.writeU16(newAddr.add(2), PROXY_PORT); // Port
var ipBytes = PROXY_IP.split('.').map(function(byte) { return parseInt(byte, 10); });
Memory.writeByteArray(newAddr.add(4), ipBytes);   
Interceptor.attach(Module.findExportByName(null, 'connect'), {
    onEnter: function(args) {
        console.log('Connected Called From:\\n' +
        Thread.backtrace(this.context, Backtracer.ACCURATE)
        .map(DebugSymbol.fromAddress).join('\\n') + '\\n');
         //Assuming the sockaddr structure is in args[1] for IPv4
         var sockaddr = args[1];
         var family = Memory.readU16(sockaddr); // AF_INET = 2
         
         if (family === 2) { // Check for IPv4
             var ip = [args[1].add(4).readU8(), 
                         args[1].add(5).readU8(), 
                         args[1].add(6).readU8(), 
                         args[1].add(7).readU8()].join('.');
             var port = args[1].add(2).readU16();
             port = ((port & 0xFF) << 8) | ((port >> 8) & 0xFF);
             console.log('Connect to ' + ip + ':' + port);
             // Overwrite the IP and port to redirect to the proxy
             // Memory.writeU16(args[1].add(2), PROXY_PORT);
             // Change the IP to the proxy IP
             // var ipBytes = PROXY_IP.split('.').map(function(byte) { return parseInt(byte, 10); });
             // Memory.writeByteArray(args[1].add(4), ipBytes);       
            if (port === 8080) {
            args[1] = newAddr;
            }
             
              var ip1 = [args[1].add(4).readU8(), 
                          args[1].add(5).readU8(), 
                          args[1].add(6).readU8(), 
                          args[1].add(7).readU8()].join('.');
              var port1 = args[1].add(2).readU16();
              port1 = ((port1 & 0xFF) << 8) | ((port1 >> 8) & 0xFF);
              console.log('Redirecting to ' + ip1 + ':' + port1);
            
             // Keep a reference to the original target to send to the proxy
             var originalTarget = ip + ':' + port +'\\n';
             this.socketFd = args[0].toInt32();
             this.test = false;
             if (port === 8080) {
                    this.test = true;
             }
             this.originalTarget = originalTarget;
        }
    },
    onLeave: function(retval) {
        console.log('Connect returned: ' + retval.toInt32());
        if (this.test) {
            console.log("Sending to proxy");
            var sendto = new NativeFunction(Module.findExportByName(null, 'send'), 'int', ['int', 'pointer', 'int', 'int']);
            var buf = Memory.allocUtf8String(this.originalTarget);
            sendto(this.socketFd, buf, this.originalTarget.length, 0);
        }
    }
});

"""

def on_message(message, data):
    print(message)


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