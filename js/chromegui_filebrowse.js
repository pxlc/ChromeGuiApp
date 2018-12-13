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

chromegui.filebrowse = {};

chromegui.filebrowse.callback_fn = null;
chromegui.filebrowse.prev_full_path = "";
chromegui.filebrowse.item_table = null;
chromegui.filebrowse.table_row_click_fn = null;

chromegui.filebrowse.set_accept_callback = function(callback_fn) {
    chromegui.filebrowse.callback_fn = callback_fn;
}

chromegui.filebrowse.set_table_row_click_callback = function(callback_fn) {
    chromegui.filebrowse.table_row_click_fn = callback_fn;
}

chromegui.filebrowse.accept = function() {
    chromegui.filebrowse.close_filebrowser();

    var full_path = $("#_filebrowse_path_input").val();
    if (chromegui.filebrowse.last_selected_row) {
        full_path = full_path + "\\" + chromegui.filebrowse.last_selected_row.name;
    }

    if (chromegui.filebrowse.callback_fn) {
        return chromegui.filebrowse.callback_fn( full_path );
    }
}

chromegui.filebrowse.open_filebrowser = function() {
    $("#_filebrowse_modal_top").css("display", "block");
}

chromegui.filebrowse.close_filebrowser = function() {
    $("#_filebrowse_modal_top").css("display", "none");
}

chromegui.filebrowse.edit_path = function() {
    var path_input_el = $("#_filebrowse_path_input");
    if (path_input_el.attr("readonly")) {
        path_input_el.attr("readonly", false);
    }
    path_input_el.focus();
}

chromegui.filebrowse.data_receiver = function(op_data) {
    if (op_data.sub_op == "path_check.exists") {
        if (op_data.sub_op_return == true) {
            var new_path = op_data.path;
            if (op_data._type == 'file') {
                new_path = op_data._parent_path;
            }
            $("#_filebrowse_path_input").val(new_path);
            chromegui.filebrowse.item_table.setData(op_data.dir_items)
        }
        else {
            $("#_filebrowse_path_input").val(chromegui.filebrowse.prev_full_path);
            $("#_filebrowse_path_alert_text").text("INVALID: " + op_data.path);
            $("#_filebrowse_path_alert_div").show();
        }
    }
}

chromegui.filebrowse.set_root = function(root_path) {
    var full_path_el = $("#_filebrowse_path_input");
    full_path_el.val(root_path);
    chromegui.to_python("filebrowse", {"sub_op": "path_check.exists", "path": full_path_el.val()});
    full_path_el.attr("readonly", true);
}

chromegui.filebrowse.init = function() {
    $("#_filebrowse_path_input").blur(function() {
        var full_path_el = $("#_filebrowse_path_input");
        if (! full_path_el.attr("readonly")) {
            chromegui.to_python("filebrowse", {"sub_op": "path_check.exists", "path": full_path_el.val()});
            full_path_el.attr("readonly", true);
        }
    });

    $("#_filebrowse_path_input").focus(function() {
        var full_path_el = $("#_filebrowse_path_input");
        if (! full_path_el.attr("readonly")) {
            chromegui.filebrowse.prev_full_path = full_path_el.val();
        }
        $('#_filebrowse_path_alert_div').hide();
    });

    $('#_filebrowse_path_input').keyup(function(e){
        var full_path_el = $("#_filebrowse_path_input");
        if(e.keyCode == 13) { // ENTER key
            // TODO: validate and accept input
            if (! full_path_el.attr("readonly")) {
                chromegui.to_python("filebrowse", {"sub_op": "path_check.exists", "path": full_path_el.val()});
            }
            full_path_el.attr("readonly", true);
        }
        else if(e.keyCode == 27) { // ESC key
            // TODO: return the text value to previous valid value
            full_path_el.attr("readonly", true);
            full_path_el.val(chromegui.filebrowse.prev_full_path);
        }
    });

    //
    // Tabulator
    //
    chromegui.filebrowse.row_last_click_time = null;
    chromegui.filebrowse.last_selected_row = null;

    // create Tabulator on DOM element with id "_filebrowse_file_list_table"
    //
    chromegui.filebrowse.item_table = new Tabulator("#_filebrowse_file_list_table", {
        height: 205, // set height of table (in CSS or here), this enables the Virtual DOM and improves render speed dramatically (can be any valid css height value)
        layout: "fitColumns", //fit columns to width of table (optional)
        selectable: 1,
        columns: [ //Define Table Columns
            {title:"Name", field:"name", width:320},
            {title:"Size", field:"size", align:"right", width:72,
                sorter: function(a, b, aRow, bRow, column, dir, sorterParams) {
                    // a, b - the two values being compared
                    // aRow, bRow - the row components for the values being compared (useful if you need to
                    //              access additional fields in the row data for the sort)
                    // column - the column component for the column being sorted
                    // dir - the direction of the sort ("asc" or "desc")
                    // sorterParams - sorterParams object from column definition array

                    var a_row_data = aRow.getData();
                    var b_row_data = bRow.getData();

                    var diff_size = a_row_data._size - b_row_data._size;
                    return diff_size; // you must return the difference between the two values
                },
            },
            {title:"Modified", field:"last_mod_dt"},
        ],
        rowClick: function(e, row) {
            var is_dbl_click = false;
            var now_time = new Date().getTime();  // this is milliseconds time
            if (chromegui.filebrowse.row_last_click_time) {
                if (now_time - chromegui.filebrowse.row_last_click_time < 500) {
                    is_dbl_click = true;
                }
            }
            chromegui.filebrowse.row_last_click_time = now_time;
            chromegui.filebrowse.last_selected_row = row.getData();

            row_data = row.getData();
            if (is_dbl_click && row_data._type == 'dir') {
                var full_path_el = $("#_filebrowse_path_input");
                var path = full_path_el.val().replace(/\\/g,"/") + "/" + row_data.name;
                chromegui.filebrowse.set_root(path);
            }

            if (chromegui.filebrowse.table_row_click_fn) {
                chromegui.filebrowse.table_row_click_fn(e, row_data, chromegui.filebrowse.item_table,
                                                        is_dbl_click);
            }
        },
    });

    //define some sample data
    var tabledata = [
        /*
        {id:1, name:"some_file.pdf", size: "405K", _size: 405000, last_mod_dt: "2018-11-23 11:45:21", _type: "file"},
        {id:2, name:"impressive_document.md", size: "2MB", _size: 2000000, last_mod_dt: "2018-11-27 15:33:12", _type: "file"},
        {id:3, name:"OTHER_FILES", size: "", _size: 0, last_mod_dt: "2018-11-29 19:02:43", _type: "dir"},
        */
    ];

    //load sample data into the table
    chromegui.filebrowse.item_table.setData(tabledata);
}


