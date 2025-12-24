from transformers import AutoTokenizer, BitsAndBytesConfig, AutoModelForCausalLM
import torch
from sqlitedb import get_connection, get_unprocessed_offers, set_interest_offer

def give_interest_to_jobs():

    conn = get_connection()
    offers = get_unprocessed_offers(conn)

    model_id = "Qwen/Qwen3-4B-Instruct-2507"

    quantization_config = BitsAndBytesConfig(load_in_8bit=True)

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype="auto",
        device_map="auto",
        quantization_config=quantization_config
    ).eval()

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    for offer in offers:
        messages = [
            {
                "role": "system",
                "content": "Tu es un filtreur d'offres d'emploi. Moi je suis une personne en recherche d'emploi ayant fini son bac+5 en informatique avec spécialité IA, j'ai 1 an d'expérience en stage, et je souhaite trouver un CDI dans le domaine de l'IA. Ta mission est de rejeter toute offre qui ne respecte pas mes limites. REJETTE SI : L'offre demande explicitement PLUS de 2 ans d'expérience; L'offre mentionne explicitement que le rôle à pourvoir est un Gouvernant, un Manager ou un Consultant; L'offre mentionne explicitement que le type de contrat n'est pas un CDI. Réponds par YES uniquement si aucune contrainte n'est franchie ou si tu n'es pas sûr, je préfère garder trop d'offres que l'inverse. Sinon, réponds NO. Ensuite explique pourquoi tu as fait ce choix"
            },
            {
                "role": "user",
                "content": f"Voici la description de l'offre : \n\n {offer["description"]}"
            }
        ]
        text = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
        )
        inputs = tokenizer([text], return_tensors="pt").to(model.device)

        with torch.inference_mode():
            outputs = model.generate(**inputs, max_new_tokens=512)

        input_length = inputs.input_ids.shape[1]
        new_tokens = outputs[0][input_length:]

        response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip().lower()
        print(f"id : {offer["id"]}")
        print(f"Résultat : {response}")
        lines = response.strip().split('\n')

        # if response == "no":
        #     set_interest_offer(conn, 2, offer["id"])
        # elif response == "yes":
        #     set_interest_offer(conn, 1, offer["id"])
        # else:
        #     print("Erreur : la réponse du modèle n'est ni 'Yes' ni 'No'")

if __name__ == "__main__":
    give_interest_to_jobs()