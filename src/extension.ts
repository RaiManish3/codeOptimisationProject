'use strict';
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    //console.log('Congratulations, your extension "codeOptimiser" is now active!');
    var sh = require("shelljs");
    var cwd = sh.pwd().toString();
    let PythonShell = require('python-shell');
    let path = require('path');
    let initials = process.env['HOME'];
    let ASTcheck = initials+'/.vscode/extensions/codeOptimisationProject/req/doASTcheck/checkAST.py';
    let ASTreplace = initials+'/.vscode/extensions/codeOptimisationProject/req/doASTreplace/replaceAST.py';
    let prnt = initials+'/.vscode/extensions/codeOptimisationProject/req/printString/in.py';
    let runge = initials+'/.vscode/extensions/codeOptimisationProject/req/printString/updateLines.py';
    let vunge = initials+'/.vscode/extensions/codeOptimisationProject/req/printString/updateOut.txt';
    let out = initials+'/.vscode/extensions/codeOptimisationProject/req/doASTreplace/output.txt';

    ASTcheck = path.relative(cwd, ASTcheck);
    ASTreplace = path.relative(cwd, ASTreplace);
    prnt = path.relative(cwd, prnt);
    runge = path.relative(cwd, runge);
    vunge = path.relative(cwd, vunge);
    out = path.relative(cwd, out)
    

    let decorationType = vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(200,30,30,0.4)'
        })    
    let disposable = vscode.commands.registerCommand('extension.check', () => {
       let editor = vscode.window.activeTextEditor;
        let fn = editor.document.fileName;
        let optionC = {
            args: [fn]
        };
        vscode.window.showInformationMessage('Please wait. Make sure your files are saved.');

    PythonShell.run(ASTcheck, optionC, function(err){
        if (err) throw err
        PythonShell.run(ASTreplace, function(drr){
            if (drr) throw err
            decorationType.dispose() 
        decorationType = vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(200,30,30,0.4)'
        })
        PythonShell.run(runge, function(err){
            if (err) throw err
            let lineReader = require('readline').createInterface({
            input: require('fs').createReadStream(vunge)
        })
        let i = 1
        let decs = []
        lineReader.on('line', function(line){
            let line_split = line.split(',')
            let pos1 = new vscode.Range(parseInt(line_split[0])-1,parseInt(line_split[1])-1,parseInt(line_split[2])-1,parseInt(line_split[3])-1)
            decs.push(pos1)
            editor.setDecorations(decorationType, decs)
            
            i += 1
        })

    })
        })
    })
        
    });



    vscode.commands.registerCommand('extension.replace', () => {
        let editor = vscode.window.activeTextEditor;
        let position = editor.selection.active
        let correctPos = new vscode.Position(position.line+1,position.character+1)
        let optionP = {
            args : [String(correctPos.line),String(correctPos.character)]
        }

        PythonShell.run(prnt, optionP, function(err, data){
            if (err || !data){
                vscode.window.showInformationMessage('String not replacable');
                return
            } 
            let arr = []
            let k = 0
            while(data[k]!=''){
                arr.push(data[k])
                k++
            }
            let dan = arr.pop()
            let ran = dan.split(',')
            arr.push('')
            k = 0
            let stri = ''
            while(arr[k]!=''){
                stri += arr[k] + '\n'
                k++
            }
            stri = stri.slice(0,-1)
            let np = new vscode.Position(Number(ran[0])-1,Number(ran[1])-1)
            let p2 = new vscode.Position(Number(ran[2])-1,Number(ran[3])-1)
            let r1 = new vscode.Range(np,p2)
            editor.edit(function(editBuilder){
                editBuilder.delete(r1)
                editBuilder.insert(np, stri)
            })
        })
    })

    context.subscriptions.push(disposable);
}

// this method is called when your extension is deactivated
export function deactivate() {
}