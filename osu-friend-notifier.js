// ==UserScript==
// @name         Osu Friend Request Notifier
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Notifies you when someone adds you as a friend on osu!
// @author       [Your Name]
// @match        https://osu.ppy.sh/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
  
    // Check for new friend requests every 5 seconds
    setInterval(checkFriendRequests, 5000);
  
    function checkFriendRequests() {
      // Get the friend request element
      const friendRequestElement = document.querySelector(
        '.user-list-item.friend-request'
      );
  
      // If a friend request exists, notify the user
      if (friendRequestElement) {
        // Get the username of the user who sent the request
        const username = friendRequestElement.querySelector(
          '.user-list-item__username'
        ).textContent;
  
        // Create a notification
        const notification = new Notification('New Friend Request!', {
          body: `${username} wants to be your friend on osu!`,
        });
  
        // Optionally, you can redirect the user to the friend request page
        // window.location.href = '/friends';
      }
    }
  })();