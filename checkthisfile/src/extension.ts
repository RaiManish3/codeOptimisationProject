'use strict';
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as fs from 'fs';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    //console.log('Congratulations, your extension "checkthisfile" is now active!');

    let decorationType = vscode.window.createTextEditorDecorationType(<vscode.DecorationRenderOptions>{
            backgroundColor: 'rgba(200,10,10,0.5)'
        })

    // The command has been defined in the package.json file
    // Now provide the implementation of the command with  registerCommand
    // The commandId parameter must match the command field in package.json
    let disposable = vscode.commands.registerCommand('extension.checkMe', () => {
        // The code you place here will be executed every time your command is executed
        let editor = vscode.window.activeTextEditor
        //let end_line = editor.document.lineCount;  //get the line count
        //let end_col = editor.document.lineAt(end_line-1).text.length; // get the column count of last line

        decorationType.dispose();
        var PythonShell = require('python-shell');
        let python_check_script = 'python_scripts/test.py';
        let inFile = 'python_scripts/testing/check1.txt'
        PythonShell.run(python_check_script, function (err) {
            if (err) throw err;
            var lineReader = require('readline').createInterface({
                input: require('fs').createReadStream(inFile)
            });

        let i = 1;
        let decs = []
        decorationType = vscode.window.createTextEditorDecorationType(<vscode.DecorationRenderOptions>{
            backgroundColor: 'rgba(200,10,10,0.5)'
        }) 
            lineReader.on('line', function (line) {
                if(i%4==0){
                    let line_split = line.split(",");  
                    let pos1 = new vscode.Range(parseInt(line_split[0]),parseInt(line_split[1]),parseInt(line_split[2]),parseInt(line_split[3]));
                    decs.push(pos1);     
                    editor.setDecorations(decorationType,decs);                  
                }
                i+=1;
            });
        });
    });

    context.subscriptions.push(disposable);
}

// this method is called when your extension is deactivated
export function deactivate() {
}