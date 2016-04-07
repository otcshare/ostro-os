/*

The MIT License (MIT)

Copyright (c) 2015 Intel Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

*/

var http = require("http");
var port = process.argv.length > 2 ? process.argv[2] : 12345;
var id   = process.argv.length > 3 ? process.argv[3] : "Sample NodeJS app";

serverFunction = function(req, resp) {
    var now = new Date().toISOString() + ": ";

    resp.writeHead(200, { "Content-Type": "text/plain" });
    resp.write(now + id + " on port " + port + "...\n");
    resp.end(now + "Requested URL was " + req.url + "\n");
}

var server = http.createServer(serverFunction)

process.stdout.write("Starting sample HTTP server on port " + port + "...\n");

server.listen(port);
