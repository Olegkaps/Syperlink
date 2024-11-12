function copyLink() {
    /* Get the text field */
    var copyText = document.getElementById("short_link");
  
    /* Select the text field */
    copyText.select();
  
    /* Copy the text inside the text field */
    document.execCommand("copy");
}