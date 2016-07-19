var mosca = require('mosca');
var mqtt = require('mqtt');

var settings = {
  port: 1883,
  persistence: mosca.persistence.Memory
};

var server = new mosca.Server(settings, function() {
    console.log('Mosca server is up and running');
});

server.on('clientConnected', function(client) {
    console.log('client connected', client.id);
});

// fired when a message is received
server.on('published', function(packet, client) {
  console.log('Published', packet.payload);
  server.on('clientDisconnected', function(client) {
    console.log('clientDisconnected');
    process.exit(0);
})
});

server.on('ready', setup);

// fired when the mqtt server is ready
function setup() {
  console.log('Mosca server is up and running');
}

client = mqtt.connect({host: 'localhost', port: 1883});
client.on('connect', function (){
    client.subscribe('presence');
    client.publish('presence', 'Hello Mqtt');
});

client.on('message', function(topic, message) {
    console.log(message.toString());
    client.end();
});
