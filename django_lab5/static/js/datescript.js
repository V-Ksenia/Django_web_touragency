document.addEventListener("DOMContentLoaded", () => {
  if (
    document.cookie.split("; ").find((row) => row.startsWith("age_verified="))
  ) {
    return;
  }

  setTimeout(() => {
    const dateOfBirth = prompt("Enter your date of birth (YYYY-MM-DD):");

    if (dateOfBirth) {
      const birthDate = new Date(dateOfBirth);
      if (isNaN(birthDate)) {
        alert("Date is incorrect. Reload the page and try again.");
        return;
      }

      const today = new Date();
      let age = today.getFullYear() - birthDate.getFullYear();
      const isBeforeBirthday =
        today.getMonth() < birthDate.getMonth() ||
        (today.getMonth() === birthDate.getMonth() &&
          today.getDate() < birthDate.getDate());

      if (isBeforeBirthday) {
        age--;
      }

      const daysOfWeek = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
      ];
      const dayOfWeek = daysOfWeek[birthDate.getDay()];

      if (age < 18) {
        alert(
          "You're underage. You need a parent's permission to use this site."
        );
      } else {
        alert(`Your age is ${age}. You were born on ${dayOfWeek}.`);
      }

      document.cookie = "age_verified=true; path=/; max-age=86400"; // 10 минут (600)
    } else {
      alert("You haven't verified your age. Please verify it later.");
    }
  }, 2000);
});
