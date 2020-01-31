// -------------------------------------------------------------------------------
// MIT License
//
// Copyright (c) 2018 pxlc@github
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
// -------------------------------------------------------------------------------

var chromegui = {};

chromegui.ws = null;

chromegui.init = function(session_id, port_num, message_fn, data_handler_fn, onopen_callback_fn) {

    chromegui.session_id = session_id;
    chromegui.port_num = port_num;
    chromegui.msg_fn = message_fn;
    chromegui.data_fn = data_handler_fn;
    chromegui.onopen_cb_fn = onopen_callback_fn;

    // Connect to Web Socket
    chromegui.ws = new WebSocket("ws://localhost:" + port_num + "/");

    // message sender - sends data to Python
    chromegui.to_python = function(op, data) {
        var msg_data = {
            "op": op,
            "session_id": chromegui.session_id,
            "data": data
        }
        var msg_data_str = JSON.stringify(msg_data);
        chromegui.ws.send(msg_data_str);
        return msg_data_str;
    };

    chromegui.close = function() {
        chromegui.ws.close();
    };

    // Set event handlers.
    chromegui.ws.onopen = function() {
        chromegui.msg_fn("onopen");
        chromegui.onopen_cb_fn();
    };
  
    // receiver of messages from Python
    chromegui.ws.onmessage = function(e) {
        // e.data contains received string ... but we only expect a JSON object string
        try {
            var data = JSON.parse(e.data);
            chromegui.data_fn(data);
        } catch(err) {
            chromegui.ws.send("[JS-ERROR]: " + err.message);
        }
    };
  
    chromegui.ws.onclose = function() {
        chromegui.msg_fn("onclose");
    };

    chromegui.ws.onerror = function(e) {
        chromegui.msg_fn("onerror");
        console.log(e)
    };
}
