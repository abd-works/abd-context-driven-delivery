
lets refactor as follows; session owns session logging 

in our host we have stateful -->
session --> set when ever a session is opened, created etc
    new (workpath, repo path, opt session path)
        workpath -> primary folder location where work is generated and read ; set when the session is opened
        repo path -> path of repo being worked in
        session-path -> where logging, and other session specific not permanant artifacts go - defaults to  repo-path/sessions/{session-name}/
        self.repo = repo tool set to repo path
    select  -> sets all logging to session variables , same as new but to exiusting
    loops 
        --> container for a discreet context, gen, eval loop ; rimary use is to demarcate boundaries in log; so we cna say x numver of log   lines were a decsreete unit if acrtivity trhart can be analysed and evaluagtfed later
        simple tool and command /loop --> incrmeent loop number; log ---loop number
        loop[number] would retureve the log entries and inject the ai chat and rtesponse under the relrevanty lines for easy analysis

   
    log() 
        <- can be called by ai or directly by code as part of running an action or on dmenad by uer /ai ; 
        use a popular python logger as a base
        guidance action run logs the action name it is given; a run with no action name leaves the log unchanged
      --logging spec
            log in sessions/{session-name}/session.log
            errors caught by host sessios/session-name/session.err

            log context --> files and folder paths being passed in;
            log the guideline, fidelity, format and actions invoked, logg hgest graph node per prqactice if known
            chat-log --> add path refertence to chat id, file name and line numbers of relevant transcript created, <-reuse then retire what u can from  prompt logging; POINT to log files, appended to log 
            log f rules were injected if so what files matched what rules only log rule names, sort and sp[earat by practidce and fidelity ]
            errors - if tools fail for ANY reason, tool , code, etc log it but dont swallow i! write fullt rce to session.err and point the log entry to a session.err line 
            log time stamp 
        

    guidance  (stories, bdd, etc)
        guidelines  -> direct reference to --> practice guidelines active only in memory, whje ever practice invoked it is set to active
            [item]
            graph <-- practice part of current graph being worked on in session 
        patterns
            pattern 