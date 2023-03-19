
let fires = [];
fires = [];
const app = new PIXI.Application({
    width: 1200, height: 768, backgroundColor: 0x1099bb, resolution: window.devicePixelRatio || 1,
});
document.body.appendChild(app.view);
const fireDuration = 100;

const camera = {
    x: 0,
    y: 0,
    theta: 0.,
    vtheta: 0,
}

const tileMap = {
    x: 300,
    y: 400,
}

const texture = PIXI.Texture.from('pixi-test/bg_grass.jpg');
const tilingSprite = new PIXI.TilingSprite(
    texture,
    app.screen.width,
    app.screen.height,
);

app.stage.addChild(tilingSprite);

function position(x, y, angle) {
    let initial = { x: x, y: y };
    let transform = { x: 0, y: 0 };    
    transform.x = (Math.cos(angle) * initial.x 
                 - Math.sin(angle) * initial.y);
    transform.y = (Math.cos(angle) * initial.y 
                 + Math.sin(angle) * initial.x);
    return transform;
}

function movecamera(car)
{
    let transform2 = position(-500, -500, -camera.theta);
   
    camera.x = car.x + transform2.x;
    camera.y = car.y + transform2.y;
    camera.vtheta += -(car.angle + camera.theta + Math.PI/2.0) * 0.004 - camera.vtheta * 0.2;
    camera.theta += camera.vtheta;
}

function turnCar(orientation) {
    car.angle += orientation * 0.1;
}

function maxToThreshold(value, threshold){
    if (Math.abs(value) > threshold) {
        return threshold * Math.sign(value);
    }
    return value;
}

window.onclick = function (event) {
      const fireSprite = PIXI.Sprite.from('pixi-test/fire.png');
      //fireSprite.scale = (0.3, 0,3);
      fireSprite.width = 15;
      fireSprite.height = 70;
      const fire = new Fire(fireSprite, car.x, car.y);
      fires.push(fire);
      app.stage.addChild(fireSprite);
};

window.onkeydown = function (event) {
      switch (event.keyCode) {
         case 37:
            car.turn(-2.0);
            break;
         case 38:
            car.accelerate();
            break;
         case 39:
            car.turn(2.0);
            break;
         case 40:
            car.break();
            break;
      }
};

class Fire {
    constructor(sprite, x, y){
        this.sprite = sprite;
        this.x = x;
        this.y = y;
        this.vy = 0;
        this.vx = 0;
        this.speed = car.speed + 10;
        this.angle = car.angle;
        this.duration = 0;
    }
    move(){
        this.vx = this.speed * Math.cos(this.angle);
        this.vy = this.speed * Math.sin(this.angle);
        this.x += this.vx;
        this.y += this.vy;
        let transform = position(this.x, this.y, camera.theta);
        let transform2 = position(-camera.x, -camera.y, camera.theta);
        this.sprite.x = transform.x + transform2.x;
        this.sprite.y = transform.y + transform2.y; 
        this.sprite.rotation = this.angle + Math.PI/2.0 + camera.theta;
        this.duration += 1;
        if (this.duration >= fireDuration) {
            app.stage.removeChild(this.sprite);
        }
    }
}

class Car {
    constructor(sprite){
        this.sprite = sprite;
        this.x = 350;
        this.y = 450;
        this.vy = 0;
        this.vx = 0;
        this.speed = 1;
        this.angle = - Math.PI/2.0;
    }
    move(){
        this.vx = this.speed * Math.cos(this.angle);
        this.vy = this.speed * Math.sin(this.angle);
        this.x += this.vx;
        this.y += this.vy;
        let transform = position(this.x, this.y, camera.theta);
        let transform2 = position(-camera.x, -camera.y, camera.theta);
        this.sprite.x = transform.x + transform2.x;
        this.sprite.y = transform.y + transform2.y; 
        this.sprite.rotation = this.angle + Math.PI/2.0 + camera.theta;
    }
    turn(orientation){
        car.angle += orientation * 0.1;
    }
    accelerate(){
        car.speed += 0.3;
    }
    break(){
        car.speed -= 0.4;
        if (car.speed < 0)
        {
            car.speed = 0;
        }
    }
}


const carSprite = PIXI.Sprite.from('pixi-test/sample.png');
carSprite.anchor.set(0.5);
carSprite.x = 100;
carSprite.y = 100;
carSprite.width = 40;
carSprite.height = 40;
const car = new Car(carSprite);
app.stage.addChild(carSprite);


let count = 0;
app.ticker.maxFPS = 50;
app.ticker.add(() => {
    count += 0.005;
    let transform2 = position(-camera.x, -camera.y, camera.theta);
    tilingSprite.tilePosition.x = transform2.x;
    tilingSprite.tilePosition.y = transform2.y;
    car.move();
    tilingSprite.tileTransform.rotation = camera.theta;
    movecamera(car);
    let counter = 0;
    for (var i = 0; i < fires.length; i++) {
        fires[i].move();
    }

    fires = fires.filter(function(value, index, arr){ 
        return value.duration < fireDuration;
    });
    // tilingSprite.tilePosition.x = car.x;
    // tilingSprite.tilePosition.y = car.y;
    //tilingSprite.tileScale.x = 2 + Math.sin(count);
    //tilingSprite.tileScale.y = 2 + Math.cos(count);

    //tilingSprite.tilePosition.x += 1;
    //tilingSprite.tilePosition.y += 1;
});



