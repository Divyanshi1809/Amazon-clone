// Online Javascript Editor for free
// Write, Edit and Run your Javascript code using JS Online Compiler

console.log("Try programiz.pro");

let marks=[56,85,44,23,26,15,13];
console.log(marks)
marks[2]=18;
console.log(marks)

//for let loop
for(let mm of marks){
    console.log(mm)
}

let items=[250,645,300,900,50];
let i=0;
for(let val of items){
    console.log(`value at index ${i}=${val}`);
    let offer=val/100;
    items[i]=items[i]-offer;
    console.log(items[i]);
    i++;
}
//for loop
for(i=0;i<items.length;i++){
    let offer=items[i]/10;
    items[i]-=offer;
}
console.log(items)
