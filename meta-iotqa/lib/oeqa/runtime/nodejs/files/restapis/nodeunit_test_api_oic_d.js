var http = require('http');
var fs = require('fs');
var path = require('path');

var options = {
    host: '127.0.0.1',
    port: 8000,
    path: '/api/oic/d',
    method: 'GET',
    headers: {
        'Accept': 'text/json'
    }
};

var apiOicD = {};
var responseJson = path.join(path.dirname(__filename), 'api_oic_d.json');

function sendHttpRequest(opts) {
    var req = http.request(opts, function(res) {
        apiOicD.statusCode = res.statusCode;
        res.setEncoding('utf8');

        res.on('data', function(data) {
            apiOicD.apiResponse = JSON.parse(data);
               fs.writeFileSync(responseJson, JSON.stringify(apiOicD));
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

function checkStrIsCsv(str) {
    var delimiter = ['.', ',', ';'];
    var result = false;

    for (var i = 0; i < delimiter.length; i++) {
        var pattern;
        if (delimiter[i] == '.') {
            pattern = '\.';
        } else {
            pattern = delimiter[i];
        }
        var isMatched = (str.indexOf(delimiter[i]) > -1) && (str.split().length == (str.match(pattern) || []).length);
        if (isMatched){
            return true;
        } else {
            result = result && isMatched;
        }
        return result;
    }
}

module.exports = {
    setUp: function(callback) {
        var content = fs.readFileSync(responseJson);
        this.apiOicD = JSON.parse(content.toString());

        callback();
    },
    tearDown: function(callback) {
        callback();
    },

    // statue code
    testApiOicDStatusCode: function(test) {
        test.strictEqual(this.apiOicD.statusCode, 200,
                        'Response is not OK!');
        test.done();
    },

    // required properties
    // n
    testApiOicDRequiredNNotNull: function(test) {
        for (var i = 0; i < this.apiOicD.apiResponse.length; i++) {
            test.ok('n' in this.apiOicD.apiResponse[i],
                    'n is not a property in the response of /api/oic/d while it is required!');
        }
        test.done();        
    },
    testApiOicDRequiredNType: function(test) {
        for (var i = 0; i < this.apiOicD.apiResponse.length; i++) {
            test.strictEqual(typeof this.apiOicD.apiResponse[i]['n'], 'string',
                            'n property is not a string!');            
        }
        test.done();
    },

    // di
    testApiOicDRequiredDiNotNull: function(test) {
        for (var i = 0; i < this.apiOicD.apiResponse.length; i++) {
            test.ok('di' in this.apiOicD.apiResponse[i],
                    'di is not a property in the response of /api/oic/d while it is required!');
        }
        test.done();
    },
    testApiOicDRequiredDiType: function(test) {
        for (var i = 0; i < this.apiOicD.apiResponse.length; i++) {
            test.strictEqual(typeof this.apiOicD.apiResponse[i]['di'], 'string',
                            'di property is not a string!');
        }
        test.done();
    },
    testApiOicDRequiredDiUuid: function(test) {
        for (var i = 0; i < this.apiOicD.apiResponse.length; i++) {
            test.ok(checkStrIsUuid(this.apiOicD.apiResponse[i]['di']),
                        'n property value is not UUID format!');
        }
        test.done();
    },

    // icv
    testApiOicDRequiredIcvNotNull: function(test) {
        for (var i = 0; i < this.apiOicD.apiResponse.length; i++) {
            test.ok('icv' in this.apiOicD.apiResponse[i],
                    'icv is not a property in the response of /api/oic/d while it is required!');
        }
        test.done();
    },
    testApiOicRequiredDIcvType: function(test) {
        for (var i = 0; i < this.apiOicD.apiResponse.length; i++) {
            test.strictEqual(typeof this.apiOicD.apiResponse[i]['icv'], 'string',
                            'icv property is not a string!');
        }
        test.done();
    },

    // optional properties
    // dmv
    testApiOicDOptionalDmvType: function(test) {
        for (var i = 0; i < this.apiOicD.apiResponse.length; i++) {
            if ('dmv' in this.apiOicD.apiResponse[i]) {
                test.strictEqual(typeof this.apiOicD.apiResponse[i]['dmv'], 'string',
                                'dmv property is not a string!');
            }
        }
        test.done();
    },
    testApiOicDOptionalDmvCsv: function(test) {
        for (var i = 0; i < this.apiOicD.apiResponse.length; i++) {
            if ('dmv' in this.apiOicD.apiResponse[i]) {
                test.ok(checkStrIsCsv(this.apiOicD.apiResponse[i]['dmv']),
                            'dmv property value is not csv format!');
            }
        }
        test.done();
    }
};
