from app.inferential.Insights import Insight


def generate_insights(data: list[dict])->list[Insight]:
    insights = []
    for item in data:
        insights.append(Insight(item["imagepath"], item["labels"], [], [], item["title"], item["content"]))
    return insights

# Example usage

data = [
    {
        "imagepath": "image1.jpg",
        "labels": ["Market", "Depression", "inflation"],
        "title": "Big depression prospect brings market down",
        "content": "The cat is enjoying the sunny afternoon."
    },
    {
        "imagepath": "image2.jpg",
        "labels": ["Dog", "Play", "Fetch"],
        "title": "A happy dog",
        "content": "The dog is playing fetch with a ball."
    },

    {
        "imagepath": "image3.jpg",
        "labels": ["Cat", "Hungry", "Meow"],
        "title": "A hungry cat",
        "content": "The cat is meowing loudly."
    }, 
    
    {
        "imagepath": "image4.jpg",
        "labels": ["feds", "money", "taxes"],
        "title": "feds",
        "content": "The federal goverment is losing money on some dummy deals"
    },

    {
        "imagepath": "image5.jpg",
        "labels": ["embassy", "international", "visa"],
        "title": "embassy",
        "content": "The international embassies are losing money on some dummy deals"
    },

    {
        "imagepath": "image6.jpg",
        "labels":  ["taxes"],
        "title": "taxes",
        "content": "you might pay less taxes next year"
    },

    {
        "imagepath": "image7.jpg",
        "labels":  ["taxes", "money"],
        "title": "taxes",
        "content": "you might pay less taxes next year"
    }
]

insights = generate_insights(data)
