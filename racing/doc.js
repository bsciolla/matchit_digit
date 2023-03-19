const canvas = document.getElementById("canvas1");
const canvasdraw = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let map = [];
let car = undefined;
let theta;
let score = 0;
let absolutescore = 20.0;
let height = 20;
let gridSize = 50;
let blockSize = 40;
let originx = 0;
let originy = 0;
let previousSelectedBlock = null;
let selectionIndex = 0;
let numberOfSorts = 26;
let gridWidth = 20;
let gridHeight = 50;
let matchingDistance = Math.max(gridWidth, gridHeight);

const mouse = {
    x: undefined,
    y: undefined
};

const camera = {
    x: 0,
    y: 0,
    theta: 0.,
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max) + 1;
    return Math.floor(Math.random() * (max - min) + min);
}

window.addEventListener("mousemove", function(e){
    mouse.x = e.x;
    mouse.y = e.y;
});

window.addEventListener("click", function(e){
    height = height * 1.2;
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    console.log("x: " + x + " y: " + y)
    blockClick(x, y);
});

function blockClick(x, y){
    let xi = Math.floor(x / gridSize);
    let yi = Math.floor(y / gridSize);
    tryFlipBlock(yi, xi);
}

function tryFlipBlock(i, j){
    if (map[i][j] !== undefined){
        selectionIndex++;      

        relateElements(previousSelectedBlock, map[i][j]);

        if (map[i][j].removed !== true){
            map[i][j].selected = selectionIndex;
            previousSelectedBlock = map[i][j];
        }
        
        if (map[i][j].color === null){
            map[i][j].color = 0;
        }
        else{
            map[i][j].color += 50;
        }
    }
}

function relateElements(block1, block2){
    if (block1 === null 
        || block2 === null
        || block1 === block2
        || block1.removed
        || block2.removed){
        return;
    }

    let possible1 = squareMatch(block1, block2);
    if (possible1){
        match(block1, block2);
    } else {
        let possible =
            followALineMatchX(block1, block2, 1)
            || followALineMatchX(block1, block2, -1)
            || followALineMatchY(block1, block2, 1)
            || followALineMatchY(block1, block2, -1);
        if (possible){
            match(block1, block2);
        }
    }
}


function followALineMatchX(block1, block2, factor){
    let possible = true;

    for (var i = 1; i <= gridWidth; i++) {
        let sourceBlock = null;
        try{
            sourceBlock = map[block1.i + i * factor][block1.j];
        }
        catch{ continue; }       
        if (sourceBlock === null
            || sourceBlock === undefined) {
            return false;
        }

        if (sourceBlock !== block1
            && sourceBlock !== block2
            && !sourceBlock.removed){
            return false;
        }
        possible = squareMatch(sourceBlock, block2);
        if (possible){
            return true;
        }
    }
}

function followALineMatchY(block1, block2, factor){
    let possible = true;

    for (var j = 1; j <= gridHeight; j++) {
        let sourceBlock = null;
        try{
            sourceBlock = map[block1.i][block1.j + j * factor];
        }
        catch{ continue; }       
        if (sourceBlock === null
            || sourceBlock === undefined) { 
            return false;
        }

        if (sourceBlock !== block1
            && sourceBlock !== block2
            && !sourceBlock.removed){
            return false;
        }
        possible = squareMatch(sourceBlock, block2);
        if (possible){
            return true;
        }
    }
}

function squareMatch(block1, block2) {
    if (block1 === null || block2 === null) { return false; }
    let imini = Math.min(block1.i, block2.i);
    let jmini = Math.min(block1.j, block2.j);

    let possible = false;
    if (block1.i === imini && block1.j === jmini
        || block2.i === imini && block2.j === jmini) {
        possible = oneWayDirectMatch(block1, block2);
    }
    else {
        possible = oneWayOtherMatch(block1, block2);
    }
    return possible;
}

function oneWayDirectMatch(block1, block2){
    let imini = Math.min(block1.i, block2.i);
    let deltai = Math.abs(block1.i - block2.i);
    let jmini = Math.min(block1.j, block2.j);
    let deltaj = Math.abs(block1.j - block2.j);
    
    let possible = 
        checkLineX(block1, block2, imini, deltai, jmini)
        && checkLineY(block1, block2, jmini, deltaj, imini + deltai);

    let possible2 = 
        checkLineX(block1, block2, imini, deltai, jmini + deltaj)
        && checkLineY(block1, block2, jmini, deltaj, imini); 
    return possible || possible2;
}

function oneWayOtherMatch(block1, block2){
    let imini = Math.min(block1.i, block2.i);
    let deltai = Math.abs(block1.i - block2.i);
    let jmini = Math.min(block1.j, block2.j);
    let deltaj = Math.abs(block1.j - block2.j);
    
    let possible = 
        checkLineX(block1, block2, imini, deltai, jmini + deltaj)
        && checkLineY(block1, block2, jmini, deltaj, imini + deltai);

    let possible2 = 
        checkLineX(block1, block2, imini, deltai, jmini)
        && checkLineY(block1, block2, jmini, deltaj, imini); 
    return possible || possible2;
}



function checkLineX(block1, block2, imini, deltai, j){
    possible = true;
    for (var i = 0; i <= deltai; i++) {
        let iblock = map[imini + i][j];
        if (iblock !== block1
         && iblock !== block2
         && !iblock.removed){
            possible = false;
        }
    }
    return possible;
}

function checkLineY(block1, block2, jmini, deltaj, i){
    possible = true;
    for (var j = 0; j <= deltaj; j++) {
        let iblock = map[i][jmini + j];
        if (iblock !== block1
         && iblock !== block2
         && !iblock.removed){
            possible = false;
        }
    }
    return possible;
}


function match(block1, block2){
    if (block1.sort !== block2.sort)
    {
        return;
    }

    block1.removed = true;
    block2.removed = true;
    block1.selected = null;
    block2.selected = null;
    previousSelectedBlock = null;
}

function turnCar(orientation) {
    car.angle += orientation * 0.1;
}

function position(x, y) {
    let transform = {
            x: (x - camera.x),
            y: (y - camera.y),
        };
        transform.x = Math.cos(camera.theta) * transform.x 
            + Math.sin(camera.theta) * transform.y;
        transform.y = Math.cos(camera.theta) * transform.y 
            - Math.sin(camera.theta) * transform.x;
    return transform;
}

window.onkeydown = function (event) {
      switch (event.keyCode) {
         case 37:
            turnCar(-1.0);
            break;
         case 38:
            originy = originy - 1;
            break;
         case 39:
            turnCar(1.0);
            break;
         case 40:
            originy = originy + 1;
            break;
      }
   };

class Car {
    constructor(x, y){
        this.x = 400;
        this.y = 400;
        this.vy = 1;
        this.vx = 0;
        this.speed = 1;
        this.angle = Math.PI/2.0;
    }
    move(){
        this.vx = this.speed * Math.cos(this.angle);
        this.vy = this.speed * Math.sin(this.angle);
        this.x += this.vx;
        this.y += this.vy;
    }
    draw(){
        let transform = position(this.x, this.y);
        let transform2 = position(this.x + 15 * Math.cos(this.angle)
            , this.y + 15 * Math.sin(this.angle));
        let color = "rgba(120,40,155,255)";
        drawRectangle(color, transform, 30);
        drawRectangle(color, transform2, 25);
    }
}

class Block {
    constructor(x, y, radius){
        this.x = x;
        this.y = y;
        this.theta = 0;
        this.phi = 0;
        this.radius = radius;
        this.color = null;
    }
    move(){
    }
    draw(){
        let transform = position(this.x, this.y);
        let color = this.color;
        if (this.removed === true){
            return;
        }
        if (this.selected === selectionIndex){
            drawVoidRectangle("rgba(255,0,255,255)", transform, this.radius);
        }
        
        if (this.sort === null){ return; }

        let green = this.coloring(0);
        let red = this.coloring(1);
        let blue = this.coloring(2);
        let green1 = this.coloring(3);
        let red1 = this.coloring(4);
        let blue1 = this.coloring(5);
        color = "rgba(" + green * 200 + ',' + red * 200 + "," + blue * 200 + "0,255)"; 
    
        drawRectangle(color, transform, this.radius);
        if (green1 + red1 + blue1 > 0){
            let innnercolor = "rgba(" + green1 * 255 + ',' + red1 * 255 + "," + blue1 * 255 + "0,255)"; 
            let innertransform = position(this.x + this.radius/4, this.y + this.radius/4);
            drawRectangle(innnercolor, innertransform, this.radius/2);
        }
    }
    coloring(rank){
        return Math.floor(this.sort / (2 ** rank) % 2);
    }
}



function drawVoidRectangle(color, transform, radius){
    canvasdraw.strokeStyle = color;
    canvasdraw.lineWidth = 2;
    canvasdraw.strokeRect(transform.x, transform.y, radius, radius);
}

function drawRectangle(color, transform, radius){
    canvasdraw.fillStyle = color;
    canvasdraw.fillRect(transform.x, transform.y, radius, radius);
}

function init(){
    console.log(Math.cos(360));
    car = new Car();
   
    for (var j = 0; j <= gridHeight; j++) {
        let row = [];
        for (var i = 0; i <= gridWidth; i++) {
            let eye = {
                x: i * gridSize + 10,
                y: j * gridSize + 10,
                radius: blockSize,
            };
            let createdBlock = new Block(eye.x, eye.y, eye.radius);
            if (Math.random() > 0.5) {createdBlock.bonus = true;}
            else {createdBlock.bonus = false;}
            
            // don't worry about i<>j here
            createdBlock.i = j;
            createdBlock.j = i;
            createdBlock.sort = getRandomInt(0, numberOfSorts);
            row[i] = createdBlock;
        }
        map[j] = row;
    }
}
function animate(){
    requestAnimationFrame(animate);
    canvasdraw.fillStyle = "rgba(255, 255, 255, 0.75)";
    canvasdraw.fillRect(0, 0, canvas.width, canvas.height);
    for (var j = 0; j <= gridHeight; j++) {
        for (var i = 0; i <= gridWidth; i++) {
            map[j][i].move();
            map[j][i].draw();           
        }
    }
    car.move();
    car.draw();
}
init();
animate();

window.addEventListener("resize", function(){
    // canvas.width = innerWidth;
    // canvas.height = innerHeight;
    // init();
})
