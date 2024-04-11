
function generateGUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
  });
}

const session_id = generateGUID()

// Function to replace 'webshop' with 'clickstream' and create WebSocket URL
function createClickstreamWebSocketURL(session_id) {
  // Dynamically get the current URL from the window object
  const currentServiceURL = `${window.location.protocol}//${window.location.host}${window.location.pathname}`;

  // Assuming the service name is in the subdomain, replace 'webshop' with 'clickstream'
  const clickstreamURL = currentServiceURL.replace('webshop', 'clickstream');

  // Decide on the WebSocket protocol based on the current protocol (http or https)
  const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';

  // Construct the WebSocket URL, excluding the 'http:' or 'https:' part from clickstreamURL
  const baseURL = clickstreamURL.substring(clickstreamURL.indexOf('//') + 2);
  const fullWSURL = `${wsProtocol}${baseURL}${session_id}`;

  return fullWSURL;
}

const socket = new WebSocket(createClickstreamWebSocketURL(session_id));


socket.addEventListener('open', function (event) {

    // Attach event listeners to the document with the throttled function
    document.addEventListener('mousemove', throttle(reportRelativePosition, 250));
    document.addEventListener('click', reportRelativePosition);
});



// Throttle function to limit the rate at which a function can fire
const throttle = (func, limit) => {
    let lastFunc;
    let lastRan;
    return function() {
      const context = this;
      const args = arguments;
      if (!lastRan) {
        func.apply(context, args);
        lastRan = Date.now();
      } else {
        clearTimeout(lastFunc);
        lastFunc = setTimeout(function() {
          if ((Date.now() - lastRan) >= limit) {
            func.apply(context, args);
            lastRan = Date.now();
          }
        }, limit - (Date.now() - lastRan));
      }
    }
  }
  
  // Throttled function for mousemove and click that reports relative coordinates
  const reportRelativePosition = function(event) {
    console.log(event);

    const payload = {
        "session_id": session_id,
        "type": event.type,
        "page_url":  window.location.href, 
        "relative_path" : window.location.pathname,
        "query_prams" : window.location.search,
        "buttons": event.buttons,
        "window": {
            "width": document.documentElement.scrollWidth,
            "height": document.documentElement.scrollHeight,
        },
        "mouse-coordinates": {
            "x": event.clientX,
            "y": event.clientY
        }
    }

    socket.send(JSON.stringify(payload));


  }; // 1000 milliseconds = 1 second
  
 
  