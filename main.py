const express = require("express");
const axios = require("axios");
const cheerio = require("cheerio");

const app = express();
const port = 3000;

// URL du site
const url = "https://ismcserver.online/your-server-ip-minecraft";

// URL du webhook Discord
const webhookUrl =
  "https://discord.com/api/webhooks/your-webhook";

// Contenu précédent
let previousContent = null;
let offlineCount = 0;

// Fonction pour envoyer le message Discord
async function sendMessage(content) {
  try {
    const data = {
      content: content,
    };
    await axios.post(webhookUrl, data);
    console.log("Contenu envoyé avec succès au webhook Discord.");
  } catch (error) {
    console.error(
      "Une erreur s'est produite lors de l'envoi du message :",
      error,
    );
  }
}

// Fonction pour vérifier et envoyer le message si nécessaire
async function checkAndSendMessage() {
  try {
    // Faire une requête GET pour récupérer le contenu HTML
    const response = await axios.get(url);

    // Vérifier si la requête a réussi
    if (response.status === 200) {
      // Utiliser Cheerio pour le parser
      const $ = cheerio.load(response.data);

      // Trouver le div avec la classe spécifiée
      const div = $(".x-fgt07z");

      // Vérifier si le div a été trouvé
      if (div.length > 0) {
        // Extraire le texte du div
        const contenu = div.text().trim();

        // Vérifier si le contenu a changé depuis la dernière fois
        if (contenu !== previousContent) {
          // Si le contenu contient "This server is offline"
          if (contenu.includes("This server is offline")) {
            if (offlineCount < 2) {
              await sendMessage("Le serveur est hors ligne");
              offlineCount++;
            }
          } else if (contenu.includes("starting.AD:")) {
            await sendMessage("Le serveur démarre");
            offlineCount = 0; // Réinitialiser le compteur si le serveur démarre
          } else if (contenu.includes("Survie entre Azyda et MisterLoulou")) {
            await sendMessage("Le serveur est en ligne");
            offlineCount = 0; // Réinitialiser le compteur si le serveur est en ligne
          }

          // Mettre à jour le contenu précédent
          previousContent = contenu;
        } else {
          console.log(
            "Le contenu n'a pas changé depuis la dernière vérification.",
          );
        }
      } else {
        console.log("Le div spécifié n'a pas été trouvé sur la page.");
      }
    } else {
      console.log("La requête GET a échoué avec le code :", response.status);
    }
  } catch (error) {
    console.error("Une erreur s'est produite :", error);
  }
}

// Exécuter la vérification toutes les 60 secondes
setInterval(checkAndSendMessage, 60000);

app.listen(port, () => {
  console.log(`Le serveur est en cours d'exécution sur le port ${port}`);
});
