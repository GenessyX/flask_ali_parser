
var modal = document.getElementById("modal");
var toggled = false;
document.getElementById("reviews").addEventListener('click', function (event) {
    // console.log("test");
    if (event.target.tagName === 'IMG' && !toggled) {
        // console.log(event.target)
        toggled = true;
        container = event.target.parentElement;
        images = container.getElementsByTagName("img");
        ind = 1;
        for (let img of images) {
            _img = img.cloneNode(true);
            if (ind > 1) {
                _img.style.display = "none";
            }
            modal.appendChild(_img);
            ind += 1;
        }
        modal.style.display = "flex";
        toggled = true;
    }
})

function close() {
    toggled = false;
    imgs = modal.getElementsByTagName("img");
    for (let img of imgs) {
        img.remove();
    }
    // modal.getElementsByTagName("img")[0].remove();
    modal.style.display = "none";
    current_index = 0;
}
modal.addEventListener('click', function (event) {
    if (event.target.id === "delete") {
        // console.log("delete");
        close();
    }
})

var current_index = 0;

function move_backwards() {
    if (current_index > 0) {
        imgs = modal.getElementsByTagName("img");
        imgs[current_index].style.display = "none";
        imgs[current_index - 1].style.display = "block";
        current_index -= 1;
    }
}

function move_forward() {
    if (current_index < modal.getElementsByTagName("img").length - 1) {
        imgs = modal.getElementsByTagName("img");
        imgs[current_index].style.display = "none";
        imgs[current_index + 1].style.display = "block";
        current_index += 1;
    }
}
document.getElementById('prev').addEventListener('click', function (event) {
    move_backwards();
})
document.getElementById('next').addEventListener('click', function (event) {
    move_forward();
})
document.addEventListener('keydown', (e) => {
    if (e.key == 'ArrowRight') {
        move_forward();
    } else if (e.key == 'ArrowLeft') {
        move_backwards();
    } else if (e.key == 'Escape') {
        if (modal.style.display != 'none') close();
    }
});
    // document.addEventListener('click', function(event) {
    //     console.log(modal.style.display)
    //     console.log(toggled);
    //     if (toggled){
    //         modal.getElementsByTagName("img")[0].remove();
    //         modal.style.display = "none";
    //         toggled = false;
    //     }
    // })