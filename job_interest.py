from transformers import AutoTokenizer, BitsAndBytesConfig, Gemma3ForCausalLM
import torch
from sqlitedb import get_connection, get_unprocessed_offers, set_interest_offer

def give_interest_to_jobs():

    conn = get_connection()
    offers = get_unprocessed_offers(conn)

    model_id = "google/gemma-3-1b-it"

    quantization_config = BitsAndBytesConfig(load_in_8bit=True)

    model = Gemma3ForCausalLM.from_pretrained(
        model_id, quantization_config=quantization_config
    ).eval()

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    for offer in offers:
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": f"Tu es un filtreur d'offres d'emploi strict. Ta mission est de rejeter (NO) toute offre qui ne respecte pas parfaitement mes limites. REJETTE AUTOMATIQUEMENT (NO) SI : L'offre demande PLUS de 2 ans d'expérience ; Le poste est orienté Gouvernance, Management ou Data Officer (je veux de la TECHNIQUE/FINE-TUNING) ; Ce n'est pas du Python. Réponds par YES uniquement si TOUTES les conditions sont réunies. Sinon, réponds NO. Réponds sous ce format : Raison du rejet : (écris la raison ici) Verdict : (YES ou NO)"}]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": f"Voici la description de l'offre : \n\n {offer["description"]}"}]
            }
        ]
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device)#.to(torch.bfloat16)


        with torch.inference_mode():
            outputs = model.generate(**inputs, max_new_tokens=64)

        input_length = inputs.input_ids.shape[1]
        new_tokens = outputs[0][input_length:]

        response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip().lower()
        print(f"id : {offer["id"]}")
        print(f"Résultat : {response}")
        lines = response.strip().split('\n')
        verdict_line = lines[-1].lower() # On prend la dernière ligne

        # if response == "no":
        #     set_interest_offer(conn, 2, offer["id"])
        # elif response == "yes":
        #     set_interest_offer(conn, 1, offer["id"])
        # else:
        #     print("Erreur : la réponse du modèle n'est ni 'Yes' ni 'No'")

if __name__ == "__main__":
    give_interest_to_jobs()