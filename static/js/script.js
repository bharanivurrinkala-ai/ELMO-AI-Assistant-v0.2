const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const fileInput = document.getElementById("file-upload");
const fileLabel = document.getElementById("selected-file");


// =========================
// ENTER TO SEND
// =========================

input.addEventListener("keydown", function(e){

    if(e.key === "Enter"){

        e.preventDefault();

        sendMessage();

    }

});



// =========================
// SCROLL
// =========================

function scrollBottom(){

    chatBox.scrollTop = chatBox.scrollHeight;

}



// =========================
// USER MESSAGE
// =========================

function addUserMessage(text){

    const div = document.createElement("div");

    div.className = "message user-message";

    div.textContent = text;


    chatBox.appendChild(div);

    scrollBottom();

}



// =========================
// ELMO MESSAGE (Fixed for Structure & Newlines)
// =========================

function addAIMessage(text){

    const div = document.createElement("div");

    div.className = "message bot-message";

    // Markdown / Newline Formatting Fix
    // 1. **bold** text ని <strong> లా మార్చుతుంది
    // 2. \n (newlines) ని <br> లా మార్చి ప్రతి పాయింట్‌ని కిందికి తీసుకువస్తుంది
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');

    div.innerHTML = formattedText;

    chatBox.appendChild(div);

    scrollBottom();

}



// =========================
// TYPING
// =========================

function typingMessage(){

    removeTyping();


    const div = document.createElement("div");

    div.className = "message bot-message";

    div.id = "typing";


    div.innerHTML = `
        ELMO is typing...
    `;


    chatBox.appendChild(div);

    scrollBottom();

}




function removeTyping(){

    const typing = document.getElementById("typing");


    if(typing){

        typing.remove();

    }

}



// =========================
// SEND MESSAGE
// =========================

async function sendMessage(){


    const message = input.value.trim();


    if(!message){

        return;

    }



    addUserMessage(message);


    input.value = "";


    typingMessage();



    try{


        const response = await fetch("/chat",{

            method:"POST",

            headers:{

                "Content-Type":"application/json"

            },

            body:JSON.stringify({

                message:message

            })

        });



        const data = await response.json();



        console.log("ELMO RESPONSE:",data);



        removeTyping();



        const answer = 
            data.response ||
            data.reply ||
            data.answer ||
            data.message;



        if(answer){

            addAIMessage(answer);

        }

        else{

            addAIMessage(
                "No response received."
            );

        }



    }


    catch(error){


        console.error(error);


        removeTyping();


        addAIMessage(
            "❌ Server connection failed."
        );


    }


}




// =========================
// FILE UPLOAD
// =========================

fileInput.addEventListener("change", async function(){


    if(fileInput.files.length === 0){

        return;

    }



    const file = fileInput.files[0];


    fileLabel.innerHTML = 
        "📄 " + file.name;



    const formData = new FormData();


    formData.append(
        "file",
        file
    );



    try{


        const response = await fetch("/upload",{

            method:"POST",

            body:formData

        });



        const data = await response.json();



        if(data.success){


            addAIMessage(
                "✅ File uploaded successfully."
            );


        }

        else{


            addAIMessage(
                "❌ Upload failed."
            );


        }


    }


    catch(error){


        console.error(error);


        addAIMessage(
            "❌ File upload error."
        );


    }


});



// =========================
// INITIAL MESSAGE
// =========================

window.onload = function(){


    if(chatBox.children.length === 0){


        addAIMessage(

            "Hello 👋 I am ELMO AI. How can I help you today?"

        );


    }


};