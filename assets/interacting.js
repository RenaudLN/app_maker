
var dx = 10
var dy = 1
var gridResize = interact.createSnapGrid({x:dx, y:dy, offset:{x:10, y:10}})
var gridDrag = interact.createSnapGrid({x:dx, y:1000, offset:{x:10, y:10}})

/////// DRAGGABLE
interact('.draggable')
  // .draggable({
  //   snap: {
  //     targets: [gridDrag],
  //     range: Infinity,
  //     relativePoints: [ { x: 0, y: 0 } ]
  //   },
  //   // enable inertial throwing
  //   inertia: false,
  //   // keep the element within the area of it's parent
  //   restrict: {
  //     restriction: "parent",
  //     endOnly: true,
  //     elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
  //   },
  //   // enable autoScroll
  //   autoScroll: false,

  //   // call this function on every dragmove event
  //   onmove: dragMoveListener,
  // })

  .resizable({
    edges: { left: false, right: true, bottom: false, top: false },
    snap: {
      targets: [gridResize],
      // range: Infinity,
      relativePoints: [ { x: 0, y: 0 } ]
    },
    restrictSize: {
      min: { width: 20, height: 20 },
    },
    restrictEdges: {
      outer: "parent",
      endOnly: false,
      elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
    }
  })
  
  .on('dragmove', function (event) {
    x += event.dx;
    y += event.dy;
  
    event.target.style.webkitTransform =
    event.target.style.transform =
        'translate(' + x + 'px, ' + y + 'px)';
    })
    
  .on('resizemove', function (event) {
    var target = event.target,
        x = (parseFloat(target.getAttribute('data-x')) || 0),
        y = (parseFloat(target.getAttribute('data-y')) || 0);

    // update the element's style
    target.style.width  = Math.round(event.rect.width/dx)*dx + 'px';
    // target.style.height = '100%';//event.rect.height + 'px';

    // translate when resizing from top or left edges
    x += event.deltaRect.left;
    y += event.deltaRect.top;

    target.style.webkitTransform = target.style.transform =
        'translate(' + x + 'px,' + y + 'px)';

    target.setAttribute('data-x', x);
    target.setAttribute('data-y', y);
  });

/////// ROW
interact('.row')
  .resizable({
    edges: { left: false, right: false, bottom: true, top: false },
    snap: {
      targets: [gridResize],
      range: Infinity,
      relativePoints: [ { x: 0, y: 0 } ]
    },
    restrictSize: {
      min: { width: 100, height: 20 },
    },
    restrictEdges: {
      outer: "parent",
      endOnly: true,
      elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
    }
  })
  
  .on('dragmove', function (event) {
    // x += event.dx;
    y += event.dy;
  
    event.target.style.webkitTransform =
    event.target.style.transform =
        'translate(' + 0 + 'px, ' + y + 'px)';
    })
    
  .on('resizemove', function (event) {
    var target = event.target,
        x = (parseFloat(target.getAttribute('data-x')) || 0),
        y = (parseFloat(target.getAttribute('data-y')) || 0);

    // update the element's style
    // target.style.width  = event.rect.width + 'px';
    target.style.height = Math.round(event.rect.height/dy)*dy + 'px';

    // translate when resizing from top or left edges
    // x += event.deltaRect.left;
    // y += event.deltaRect.top;

    target.style.webkitTransform = target.style.transform =
        'translate(' + 0 + 'px,' + y + 'px)';

    target.setAttribute('data-x', x);
    target.setAttribute('data-y', y);
  });


function dragMoveListener (event) {
  var target = event.target,
      // keep the dragged position in the data-x/data-y attributes
      x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx,
      y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

  // translate the element
  target.style.webkitTransform =
  target.style.transform =
    'translate(' + x + 'px, ' + y + 'px)';

  // update the posiion attributes
  target.setAttribute('data-x', x);
  target.setAttribute('data-y', y);
}

// this is used later in the resizing and gesture demos
window.dragMoveListener = dragMoveListener;

x = 10, y = 10;


// document.addEventListener('click', function(e) {
//   e = e || window.event;
//   var target = e.target || e.srcElement,
//       text = target.textContent || target.innerText;
//   var dummy = document.getElementById('dummy')
//   console.log(target.id)
//   dummy.setAttribute('data-focus', target.id)
// }, false);