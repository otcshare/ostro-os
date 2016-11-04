var http = require('http');
var fs = require('fs');
var path = require('path');

var options = {
    host: '127.0.0.1',
    port: 8000,
    path: '/api/oic/p',
    method: 'GET',
    headers: {
        'Accept': 'text/json'    
    }    
};

var apiOicP = {};
var responseJson = 'api_oic_p.json';

function sendHttpRequest(opts) {
    var req = http.request(opts, function(res) {    
        apiOicP.statusCode = res.statusCode;
        res.setEncoding('utf8');
        
        res.on('data', function(data) {
            apiOicP.apiResponse = JSON.parse(data);
               fs.writeFileSync(responseJson, JSON.stringify(apiOicP)); 
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
        this.apiOicP = JSON.parse(content.toString());
            
        callback();
    },
    tearDown: function(callback) {        
        callback();        
    },
    
    // statue code
    testApiOicPStatusCode: function(test) {
        test.strictEqual(this.apiOicP.statusCode, 200, 
                        'Response is not OK!');
        test.done();            
    },        
    
    // required properties
    // pi
    testApiOicPRequiredPiNotNull: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            test.ok('pi' in this.apiOicP.apiResponse[i],
                    'pi is not a property in the response of /api/oic/p while it is required!');
        }
        test.done();
    },
    testApiOicPRequiredPiType: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            test.strictEqual(typeof this.apiOicP.apiResponse[i]['pi'], 'string',                         
                            'pi property is not a string!');
        }
        test.done();
    },
    
    // mnmn
    testApiOicPRequiredMnmnNotNull: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            test.ok('mnmn' in this.apiOicP.apiResponse[i], 
                    'mnmn is not a property in the response of /api/oic/p while it is required!');
        }
        test.done();
    },
    testApiOicPRequiredMnmnType: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            test.strictEqual(typeof this.apiOicP.apiResponse[i]['mnmn'], 'string',                         
                            'mnmn property is not a string!');
        }
        test.done();
    },
    
    // optional properties
    // mnml
    testApiOicPOptionalMnmlType: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            if ('mnml' in this.apiOicP.apiResponse) {
                test.strictEqual(typeof this.apiOicP.apiResponse[i]['mnml'], 'string',
                                'mnml property is not a string!');
            }            
        }
        test.done();
    },
    // mnmo
    testApiOicPOptionalMnmoType: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            if ('mnmo' in this.apiOicP.apiResponse) {
                test.strictEqual(typeof this.apiOicP.apiResponse[i]['mnmo'], 'string',
                                'mnmo property is not a string!');
            }            
        }
        test.done();
    },    
    // mndt
    testApiOicPOptionalMndtType: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            if ('mndt' in this.apiOicP.apiResponse) {
                test.strictEqual(typeof this.apiOicP.apiResponse[i]['mndt'], 'string',
                                'mndt property is not a string!');
            }       
        }
        test.done();
    },    
    // mnpv
    testApiOicPOptionalMnpvType: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            if ('mnpv' in this.apiOicP.apiResponse) {
                test.strictEqual(typeof this.apiOicP.apiResponse[i]['mnpv'], 'string',
                                'mnpv property is not a string!');
            }       
        }
        test.done();
    },
    // mnos
    testApiOicPOptionalMnosType: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            if ('mnos' in this.apiOicP.apiResponse) {
                test.strictEqual(typeof this.apiOicP.apiResponse[i]['mnos'], 'string',
                                'mnos property is not a string!');
            }
        }
        test.done();
    },
    // mnhw
    testApiOicPOptionalMnhwType: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            if ('mnhw' in this.apiOicP.apiResponse) {
                test.strictEqual(typeof this.apiOicP.apiResponse[i]['mnhw'], 'string',
                                'mnhw property is not a string!');
            }
        }
        test.done();
    },  
    // mnfv
    testApiOicPOptionalMnfvType: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            if ('mnfv' in this.apiOicP.apiResponse) {
                test.strictEqual(typeof this.apiOicP.apiResponse[i]['mnfv'], 'string',
                                'mnfv property is not a string!');
            }
        }
        test.done();
    },       
    // mnsl
    testApiOicPOptionalMnslType: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            if ('mnsl' in this.apiOicP.apiResponse) {
                test.strictEqual(typeof this.apiOicP.apiResponse['mnsl'], 'string',
                                'mnsl property is not a string!');       
            }
        }
        test.done();
    },      
    // st
    testApiOicPOptionalStType: function(test) {
        for (var i = 0; i < this.apiOicP.apiResponse.length; i++) {
            if ('st' in this.apiOicP.apiResponse) {
                test.strictEqual(typeof this.apiOicP.apiResponse['st'], 'string',
                                'st property is not a string!');
            }
        }
        test.done();
    },          
};
