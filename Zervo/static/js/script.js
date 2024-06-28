const videoElement = document.querySelector('video');
const playPauseButton = document.querySelector('button');
const playButtonElement = document.querySelector('.playbutton'); // Select the playbutton element

playPauseButton.addEventListener('click', () => {
  playPauseButton.classList.toggle('playing');
  if (playPauseButton.classList.contains('playing')) {
    videoElement.play();
  } else {
    videoElement.pause();
  }

  // Check if the playbutton element exists and remove it
  if (playButtonElement) {
    playButtonElement.remove();
  }
});

videoElement.addEventListener('ended', () => {
  playPauseButton.classList.remove('playing');
});

const menuToggle = document.querySelector('.toggle');
const showcase = document.querySelector('.showcase');

menuToggle.addEventListener('click', () => {
  menuToggle.classList.toggle('active');
  showcase.classList.toggle('active');
});
