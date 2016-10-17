var http = require('http');
var fs = require('fs');
var os = require('os');
var path = require('path');

var options = {
    host: '127.0.0.1',
    port: 8000,
    path: '/api/system',
    method: 'GET',
    headers: {
        'Accept': 'text/json'
    }
};

var apiSystem = {};
var responseJson = path.join(path.dirname(__filename), 'api_system.json');

function sendHttpRequest(opts) {
    var req = http.request(opts, function (res) {
        apiSystem.statusCode = res.statusCode;
        res.setEncoding('utf8');
        
        res.on('data', function(data) {
            apiSystem.apiResponse = JSON.parse(data);
               fs.writeFileSync(responseJson, JSON.stringify(apiSystem)); 
        });
    });
    req.end();
}

// First generate HTTP response file. Only node script will generate the
// json format response.
if (process.argv[1] == __filename) {
    sendHttpRequest(options);
}

module.exports = {
    setUp: function(callback) {
        var content = fs.readFileSync(responseJson);
        this.apiSystem = JSON.parse(content.toString());
            
        callback();          
    },
    tearDown: function(callback) {        
        callback();        
    },
    
    // statue code
    testApiSystemStatusCode: function(test) {
        test.strictEqual(this.apiSystem.statusCode, 200, 
                        'Response is not OK!');
        test.done();            
    },
    
    // hostname
    testApiSystemHostnameNotNull: function(test) {
        test.ok('hostname' in this.apiSystem.apiResponse, 
                    'hostname is not a property in the response of /api/system!');
        test.done();
    },
    testApiSystemHostnameType: function(test) {
        test.strictEqual(typeof this.apiSystem.apiResponse['hostname'], 'string',                         
                        'hostname property is not string!');
        test.done();
    },
    testApiSystemHostnameValue: function(test) {
        test.strictEqual(this.apiSystem.apiResponse['hostname'], os.hostname(),  
                        'local hostname value differs from the one from api response!');
        test.done();
    },
    
    // type
    testApiSystemTypeNotNull: function(test) {
        test.ok('type' in this.apiSystem.apiResponse,
                    'type is not a property in the response of /api/system!');
        test.done();                        
    },
    testApiSystemTypeType: function(test) {
        test.strictEqual(typeof this.apiSystem.apiResponse['type'], 'string',
                        'type property is not string!');
        test.done();                            
    },
    testApiSystemTypeValue: function(test) {
        test.strictEqual(this.apiSystem.apiResponse['type'], os.type(),                        
                        'local type value differs from the one from api response!');
        test.done();
    },

    // arch    
    testApiSystemArchNotNull: function (test) {
        test.ok('arch' in this.apiSystem.apiResponse,
                    'arch is not a property in the response of /api/system!');
        test.done();
    },
    testApiSystemArchType: function(test) {
        test.strictEqual(typeof this.apiSystem.apiResponse['arch'], 'string',
                    'arch property is not string!');
        test.done();                   
    },
    testApiSystemArchValue: function (test) {
        test.strictEqual(this.apiSystem.apiResponse['arch'], os.arch(),
                        'local arch value differs from the one from /api/system!');
        test.done();                              
    },
    
    // release
    testApiSystemReleaseNotNull: function(test) {
        test.ok('release' in this.apiSystem.apiResponse,
                    'release is not a property in the response of /api/system!');
        test.done();
    },
    testApiSystemReleaseType: function(test) {
        test.strictEqual(typeof this.apiSystem.apiResponse['release'], 'string',
                    'release property is not a string!');
        test.done();                   
    },
    testApiSystemReleaseValue: function (test) {
        test.strictEqual(this.apiSystem.apiResponse['release'], os.release(),
                        'local release value differs from the one from /api/system!');
        test.done();
    },
    
    // uptime     
    testApiSystemUptimeNotNull: function(test) {
        test.ok('uptime' in this.apiSystem.apiResponse,
                    'uptime is not a property in the response of /api/system!');
        test.done();
    },
    testApiSystemUptimeType: function(test) {
        test.strictEqual(typeof this.apiSystem.apiResponse['uptime'], 'number',
                    'uptime property is not a number!');
        test.done();                   
    },
    
    // loadavg
    testApiSystemLoadavgNotNull: function(test) {
        test.ok('loadavg' in this.apiSystem.apiResponse,
                    'loadavg is not a property in the response of /api/system!');
        test.done();
    },
    testApiSystemLoadavgType: function(test) {
        test.strictEqual(typeof this.apiSystem.apiResponse['loadavg'], 'object',
                    'loadavg property is not an array!');
                    
        for (var i = 0; i < this.apiSystem.apiResponse['loadavg'].length; i++) {
            test.strictEqual(typeof this.apiSystem.apiResponse['loadavg'][i], 'number',
                            'some item in loadavg property is not a number!');    
        }                    
        test.done();
    },
    
    // totalmem
    testApiSystemTotalmemNotNull: function(test) {
        test.ok('totalmem' in this.apiSystem.apiResponse,
                    'totalmem is not a property in the response of /api/system!');
        test.done();
    },
    testApiSystemTotalmemType: function(test) {
        test.strictEqual(typeof this.apiSystem.apiResponse['totalmem'], 'number',
                    'totalmem property is not a string!');
        test.done(); 
    },
    testApiSystemTotalmemValue: function (test) {
        test.strictEqual(this.apiSystem.apiResponse['totalmem'], os.totalmem(),
                        'local totalmem value differs from the one from /api/system!');
        test.done();
    }, 
    
    // freemem
    testApiSystemFreememNotNull: function(test) {
        test.ok('freemem' in this.apiSystem.apiResponse,
                    'freemem is not a property in the response of /api/system!');
        test.done();
    },
    testApiSystemFreememType: function(test) {
        test.strictEqual(typeof this.apiSystem.apiResponse['freemem'], 'number',
                    'freemem property is not a string!');
        test.done(); 
    },

    // cpus
    testApiSystemCpusNotNull: function(test) {
        test.ok('cpus' in this.apiSystem.apiResponse,
                    'cpus is not a property in the response of /api/system!');
        test.done();
    },
    testApiSystemCpusType: function(test) {
        test.strictEqual(typeof this.apiSystem.apiResponse['cpus'], 'object',
                    'cpus property is not an array!');
        test.done(); 
    },
    testApiSystemCpusValue: function (test) {
        var localCpus = os.cpus();
        for (var i = 0; i < this.apiSystem.apiResponse['cpus'].length; i++) {        
            test.strictEqual(typeof this.apiSystem.apiResponse['cpus'][i]['model'], 'string',
                            'cpus.model proerty is not string!');
            test.strictEqual(typeof this.apiSystem.apiResponse['cpus'][i]['speed'], 'number',
                            'cpus.speed proerty is not number!');
            test.strictEqual(this.apiSystem.apiResponse['cpus'][i]['model'], localCpus[i]['model'],
                            'local cpus.model value differs from the one from /api/system!');                                                  
        }
        test.done();
    },
    
    // network interfaces
    testApiSystemNetworkInterfacesValue: function(test) {
        var localNetworkInterfaces = os.networkInterfaces();
        test.deepEqual(this.apiSystem.apiResponse['networkinterfaces'], localNetworkInterfaces,
                                'local network interfaces differs from the one from /api/system!');
        test.done();
    } 
};
