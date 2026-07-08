function sendMessage() {


    let input = document.getElementById("user-input");

    let message = input.value.trim();


    if(message === ""){
        return;
    }


    let chatBox = document.getElementById("chat-box");



    // User message

    let userMessage = document.createElement("div");

    userMessage.className = "message user-message";

    userMessage.innerHTML = message;


    chatBox.appendChild(userMessage);



    input.value = "";



    // Thinking animation

    let thinking = document.createElement("div");

    thinking.className = "message bot-message";

    thinking.innerHTML = "ELMO is thinking... 🤖";


    chatBox.appendChild(thinking);



    chatBox.scrollTo({

        top: chatBox.scrollHeight,

        behavior:"smooth"

    });



    fetch("/chat",{


        method:"POST",


        headers:{

            "Content-Type":"application/json"

        },


        body:JSON.stringify({

            message:message

        })


    })



    .then(response => response.json())


    .then(data => {


        thinking.remove();



        let botMessage = document.createElement("div");


        botMessage.className="message bot-message";



        botMessage.innerHTML = data.reply

        .replace(/\*\*(.*?)\*\*/g,"<b>$1</b>")

        .replace(/## (.*?)/g,"<h3>$1</h3>")

        .replace(/\n/g,"<br>");



        chatBox.appendChild(botMessage);



        chatBox.scrollTo({

            top:chatBox.scrollHeight,

            behavior:"smooth"

        });



    })



    .catch(error=>{


        thinking.innerHTML="Something went wrong ❌";


    });



}


// Enter key support

document.getElementById("user-input")
.addEventListener("keypress",function(event){


    if(event.key==="Enter"){

        sendMessage();

    }


});