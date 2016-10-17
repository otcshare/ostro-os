var http = require('http');
var fs = require('fs');
var path = require('path');

var options = {
    host: '127.0.0.1',
    port: 8000,
    path: '/api/oic/res',
    method: 'GET',
    headers: {
        'Accept': 'text/json'    
    }    
};

var apiOicRes = {};
var responseJson = path.join(path.dirname(__filename), 'api_oic_res.json');

function sendHttpRequest(opts) {
    var req = http.request(opts, function(res) {    
        apiOicRes.statusCode = res.statusCode;
        res.setEncoding('utf8');
        
        res.on('data', function(data) {
            apiOicRes.apiResponse = JSON.parse(data);
               fs.writeFileSync(responseJson, JSON.stringify(apiOicRes)); 
        });
    });
    req.end();
}

// First generate HTTP response file. Only node script will generate the
// json format response.
if (process.argv[1] == __filename) {
    sendHttpRequest(options);
}

function checkStrIsUuid(str) {
    var uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidPattern.test(str);
}

module.exports = {
    setUp: function(callback) {
        var content = fs.readFileSync(responseJson);
        this.apiOicRes = JSON.parse(content.toString());
            
        callback();
    },
    tearDown: function(callback) {        
        callback();        
    },
    
    // statue code
    testApiOicResStatusCode: function(test) {
        test.strictEqual(this.apiOicRes.statusCode, 200, 
                        'Response is not OK!');
        test.done();            
    },   
    
    // n
    testApiOicResNType: function(test) {
        for (var i = 0; i < this.apiOicRes.apiResponse.length; i++) {
            if ('n' in this.apiOicRes.apiResponse[i]) {
                test.strictEqual(typeof this.apiOicRes.apiResponse[i]['n'], 'string',                         
                                'n property is not a string!');
            }
        }
        test.done();
    },     

    // di
    testApiOicResDiType: function(test) {
        for (var i = 0; i < this.apiOicRes.apiResponse.length; i++) {
            if ('di' in this.apiOicRes.apiResponse[i]) {
                test.strictEqual(typeof this.apiOicRes.apiResponse[i]['di'], 'string',                         
                                'di property is not a string!');
            }                        
        }                        
        test.done();
    },  
    testApiOicResDiUuid: function(test) {
        for (var i = 0; i < this.apiOicRes.apiResponse.length; i++) {     
            if ('di' in this.apiOicRes.apiResponse[i]) {       
                test.ok(checkStrIsUuid(this.apiOicRes.apiResponse[i]['di']), 
                            'di property value is not UUID format!');                    
            }                        
        }                    
        test.done();
    },    
    
    // links
    testApiOicResLinksType: function(test) {
        for (var i = 0; i < this.apiOicRes.apiResponse.length; i++) {        
            if ('links' in this.apiOicRes.apiResponse[i]) {        
                test.strictEqual(Object.prototype.toString.call(this.apiOicRes.apiResponse[i]['links']), '[object Array]',
                                    'links property is not an array!');    
            }                                
        }
        test.done();
    }, 
};
