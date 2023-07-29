const messageContainer = document.getElementById('messageContainer');
const resetButton = document.getElementById('resetButton');

function displayUserMessage(message) {
  const userMessage = `
    <div class="message user-message">
      ${message}
    </div>
  `;
  messageContainer.innerHTML += userMessage;
}

function displaySystemMessage(message) {
  const systemMessage = `
    <div class="message system-message">
      ${message}
    </div>
  `;
  messageContainer.innerHTML += systemMessage;
}

function displayOptions(vegetableName, options) {
  const buttonHTML = options.map(option => `<button onclick="handleOptionClick('${vegetableName}', '${option}')">${option}</button>`).join(' ');
  const systemMessage = `
    <div class="system-message">
      <strong>Choose an option:</strong><br>
      ${buttonHTML}
    </div>
  `;
  displaySystemMessage(systemMessage);
}

function displayOptionDetails(option, value) {
  const systemMessage = `
    <div class="system-message">
      <strong>${option}:</strong> ${value}
    </div>
  `;
  displaySystemMessage(systemMessage);
}

function sendMessage() {
  const userInput = document.getElementById('userInput');
  const userMessage = userInput.value.trim();

  if (userMessage === '') {
    return;
  }

  displayUserMessage(userMessage);
  processUserMessage(userMessage);

  userInput.value = '';
  resetButton.disabled = false;
}

function processUserMessage(message) {
  const vegetableName = message.toLowerCase();

  fetch(`/get_option_details?vegetable=${vegetableName}&option=price`)
    .then(response => response.json())
    .then(data => {
      if ('price' in data) {
        const options = ['Price', 'Market', 'Season', 'NextYearPrice'];
        displayOptions(vegetableName, options);
      } else {
        displaySystemMessage(`No details found for '${message}'`);
      }
    })
    .catch(error => {
      console.log('Error:', error);
    });
}

function handleOptionClick(vegetableName, option) {
  fetch(`/get_option_details?vegetable=${vegetableName}&option=${option}`)
    .then(response => response.json())
    .then(data => {
      displayOptionDetails(option, data[option]);
    })
    .catch(error => {
      console.log('Error:', error);
    });
}

const userInput = document.getElementById('userInput');
userInput.addEventListener('keydown', function(event) {
  if (event.key === 'Enter') {
    sendMessage();
  }
});

function resetChat() {
  messageContainer.innerHTML = '';
  resetButton.disabled = true;
}



function sendAnalysisRequest() {
  const userInput = document.getElementById('userInput');
  const commodity = userInput.value.trim();
  const year = prompt("Enter the year for analysis:");

  if (commodity === '') {
    return;
  }

  fetch('/analysis', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `commodity=${commodity}&year=${year}`,
  })
  .then(response => response.text())
  .then(html => {
    document.open();
    document.write(html);
    document.close();
  });
  
  userInput.value = '';
  resetButton.disabled = false;
}
//anaysis
$(document).ready(function() {
  // Toggle the form display and Go Back button visibility when the Three-dot button is clicked
  $("#toggleForm").click(function() {
    $("#formContainer").collapse("toggle");
    $("#goBackButton").toggle();

    // Hide the generated plot when going back to the form
    $("#plotImage").remove();
    $("#resetButton").hide();
    $("#analyzeButton").prop("disabled", true);
  });

  // Disable the "Analyze" button if either commodity or year is empty
  function updateAnalyzeButton() {
    const commodityValue = $("#commodity").val().trim();
    const yearValue = $("#year").val().trim();
    const analyzeButton = $("#analyzeButton");

    if (commodityValue === "" || yearValue === "") {
      analyzeButton.prop("disabled", true);
      $("#plotImage").remove();
      $("#resetButton").hide();
    } else {
      analyzeButton.prop("disabled", false);
    }
  }

  $("#commodity, #year").keyup(updateAnalyzeButton);

  // Reset the plot when the "Reset" button is clicked
  $("#resetButton").click(function() {
    $("#plotImage").remove();
    $("#resetButton").hide();
  });

  // Call the function on page load
  updateAnalyzeButton();
});
