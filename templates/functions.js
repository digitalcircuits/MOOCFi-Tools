let pingAliveStatus = false;

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function retCompAssn() {
    document.getElementById("statusID").setAttribute("style", "display: none");
    document.getElementById("statusText").setAttribute("style", "display: none");
    
    const tbody = document.querySelector('tbody');
    const currentRows = tbody.childNodes;

    currentRows.forEach((row, i) => {
        if(row['nodeName'] != '#text') {
            /* 
            For some reason, looping through each row, a #text is always 
            the first result which messes up the function so this step skips it
            */
            setTimeout(() => {
                /* 
                Dont request all 200+ assignment status at once
                */
                const [id, name, stat, dwnbtn, dwncompbtn] = row.childNodes;
                fetch(`${window.location.origin}/retCompAssnById?exer_id=${id.innerText}`)
                .then(resp => resp.json())
                .then(resp => {
                    if(resp['completed'] == 1) {
                        stat.innerHTML = ` <a type="button" rel="noopener noreferrer" href="${window.location.origin}/download_template?exer_id=${id.innerText}" class="btn btn-success"><i class="fas fa-download"></i> Download Template</a> `;
                        dwnbtn.innerHTML = ` <a type="button" rel="noopener noreferrer" href="${window.location.origin}/download_suggestion?exer_id=${id.innerText}" class="btn btn-success"><i class="fas fa-download"></i> Download Suggested Answer</a> `;
                        dwncompbtn.innerHTML = ` <a type="button" rel="noopener noreferrer" href="${window.location.origin}/download_success?exer_id=${id.innerText}" class="btn btn-success"><i class="fas fa-download"></i> Download Your Submitted Answer</a> `;
                    }
                    else if(resp['completed'] == 0) {
                        stat.innerHTML = ' <button type="button" class="btn btn-danger"><i class="fas fa-times-circle"></i> Not Completed</button> ';
                        dwnbtn.innerHTML = ' <button type="button" class="btn btn-danger"><i class="fas fa-times-circle"></i> Not Completed</button> ';
                        dwncompbtn.innerHTML = ' <button type="button" class="btn btn-danger"><i class="fas fa-times-circle"></i> Not Completed</button> ';
                    }
                })
            }, i * 1000)
        }

      })

}

function retAllAssn() {
    /* Get All Assignments */
    document.getElementById("statusID").setAttribute("src", "./img/loading.gif")
    document.getElementById("statusText").textContent = "Fetching All Assignments... Please Wait..."

    console.log("Getting all assignments");


    fetch(`${window.location.origin}/retAllAssn`)
    .then(resp =>resp.json())
    .then(resp => {
        const tbody = document.querySelector('tbody');
        let all_res = resp['all_assignments'];
        for(let key in all_res) {
            const row = document.createElement('tr');
            const id = document.createElement('td');
            const name = document.createElement('td');
            const status = document.createElement('td');
            const dsug = document.createElement('td');
            const dcomp = document.createElement('td');
            id.textContent = key;
            name.textContent = all_res[key];
            status.innerHTML = ' <button type="button" class="btn btn-secondary">Fetching Status</button> ';
            dsug.innerHTML = ' <button type="button" class="btn btn-secondary">Fetching Status</button> ';
            dcomp.innerHTML = ' <button type="button" class="btn btn-secondary">Fetching Status</button> ';
            row.appendChild(id);
            row.appendChild(name);
            row.appendChild(status);
            row.appendChild(dsug);
            row.appendChild(dcomp);
            tbody.appendChild(row);
        }
    })
    .then(retCompAssn)
    .catch(err => {

        pingAliveStatus = false;
        document.getElementById("server-not-online-url").textContent = `Error While Attempting to Load All Assignments: ${err}`;
        document.getElementById("server-not-online").setAttribute("style", 'display: inline;')
        document.getElementById("server-not-login").setAttribute("style", 'display: none;')  
        document.getElementById("server-error-msg").setAttribute("style", 'display: none;')

    })
    
}

function pingAlive() {

    fetch(`${window.location.origin}/pingServer`)
    .then(response => response.json())
    .then(response => {
        /* Check to see if we can connect to the TMC servers */
        if(response['tmc'] == 0) {
            pingAliveStatus = false;
            document.getElementById("server-error-msg").textContent = response['msg'];
            document.getElementById("server-error-msg").setAttribute("style", 'display: inline;')
            document.getElementById("server-not-login").setAttribute("style", 'display: none;')
            document.getElementById("server-not-online").setAttribute("style", 'display: none;')
        }
        /* Check to see if we are still logged in */
        else if(response['login'] == 0) {
            pingAliveStatus = false;
            document.getElementById("server-not-login").setAttribute("style", 'display: inline;')
            document.getElementById("server-error-msg").setAttribute("style", 'display: none;')
            document.getElementById("server-not-online").setAttribute("style", 'display: none;')
        }
        /* If we can connect to the server, and it reports no problems, hide all the errors*/
        else if(response['status'] == 1 && response['login'] == 1 && response['tmc'] == 1) {
            pingAliveStatus = true;
            document.getElementById("server-external-error").setAttribute("style", 'display: none;')
            document.getElementById("server-not-online").setAttribute("style", 'display: none;')
            document.getElementById("server-not-login").setAttribute("style", 'display: none;')  
        }
    }).catch(err => {
        /* If we are having network issues, that may indicate the server is offline*/
        pingAliveStatus = false;
        document.getElementById("server-not-online-url").textContent = window.location.origin;
        document.getElementById("server-not-online").setAttribute("style", 'display: inline;')
        document.getElementById("server-not-login").setAttribute("style", 'display: none;')  
        document.getElementById("server-error-msg").setAttribute("style", 'display: none;')
    })

}

function jumpTop() {
    /* If theres an error, jump to the top of the page so the user can see it*/
    if(pingAliveStatus == False) {
        window.scrollTo({ top: 0, behavior: `smooth` })
    }
}

function login() {
    document.getElementById("logging-in-attempt").setAttribute("style", "display: block;");
    document.getElementById("logging-in-success").setAttribute("style", "display: none;");
    document.getElementById("logging-in-failed").setAttribute("style", "display: none;");

    let formData = new FormData();
    formData.append("username", document.getElementById("login-moocfi-panel-email").value);
    formData.append("password", document.getElementById("login-moocfi-panel-pass").value);
    formData.append("user_agent", navigator.userAgent)

    fetch(`${window.location.origin}/login`, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(response => {
        if (response['status'] == 1) {
            document.getElementById("logging-in-attempt").setAttribute("style", "display: none;");
            document.getElementById("logging-in-success").setAttribute("style", "display: block;");
            sleep(3000).then(() => { window.location.replace(`${window.location.origin}/panel`); });
        } else if(response['status'] == 0) {
            document.getElementById("logging-in-attempt").setAttribute("style", "display: none;");
            document.getElementById("logging-in-failed").setAttribute("style", "display: block;");
            document.getElementById("text-error-msg-login").textContent = response['msg'];
        }
    }).catch(response => {
            document.getElementById("logging-in-attempt").setAttribute("style", "display: none;");
            document.getElementById("logging-in-failed").setAttribute("style", "display: block;");
            document.getElementById("text-error-msg-login").textContent = response;
    })
}

