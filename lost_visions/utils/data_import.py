from lost_visions import models

__author__ = 'ubuntu'


def add_irish_life_linked_images():

    to_link = {
        "11126612333":
            [
                {
                    "name": "The Meeting Of Ned And Kathleen",
                    "file": "PAGE 182 The Meeting Of Ned And Kathleen.jpg"
                }
            ],
        "11123139574":
            [
                {
                    "name": "Farmer O'Shaughnessy" ,
                    "file": "PAGE 14 Farmer O'Shaughnessy.jpg"
                },
                {
                    "name": "Farmer O'Shaughnessy Reverse Note",
                    "file": "PAGE 14 Farmer O'Shaughnessy Reverse Note.jpg"
                }
            ],
        "11122550103":
            [
                {
                    "name": "Mrs Moriarty's Appeal To Fr. Burke" ,
                    "file": "PAGE 22 Mrs Moriarty's Appeal To Fr. Burke.jpg"
                },
                {
                    "name": "Mrs Moriarty's Appeal To Fr. Burke Reverse Note",
                    "file": "PAGE 22 Mrs Moriarty's Appeal To Fr. Burke Reverse Note.jpg"
                }
            ],
        "11123797044":
            [
                {
                    "name": "The Mitchellstown Caves" ,
                    "file": "PAGE 30 The Mitchellstown Caves.jpg"
                },
                {
                    "name": "The Mitchellstown Caves Reverse Note",
                    "file": "PAGE 30 The Mitchellstown Caves Reverse Note.jpg"
                }
            ],
        "11126097286":
            [
                {
                    "name": "The Deliverence" ,
                    "file": "PAGE 54 The Deliverence.jpg"
                },
                {
                    "name": "The Deliverence Reverse Note",
                    "file": "PAGE 54 The Deliverence Reverse Note.jpg"
                }
            ],
        "11127443786":
            [
                {
                    "name": "Phelim McCarthy" ,
                    "file": "PAGE 94 Phelim McCarthy.jpg"
                },
                {
                    "name": "Phelim McCarthy Reverse Note & Drawing",
                    "file": "PAGE 94 Phelim McCarthy Reverse Note & Drawing.jpg"
                }
            ],
        "11121871366":
            [
                {
                    "name": "The Present To McCarthy" ,
                    "file": "PAGE 98 The Present To McCarthy.jpg"
                },
                {
                    "name": "The Present To McCarthy Reverse Note",
                    "file": "PAGE 98 The Present To McCarthy Reverse Note.jpg"
                }
            ],
        "11122038386":
            [
                {
                    "name": "Phelim's Visit To The Hovel",
                    "file": "PAGE 106 Phelim's Visit To The Hovel.jpg"
                },
                {
                    "name": "Phelim's Visit To The Hovel Reverse Note",
                    "file": "PAGE 106 Phelim's Visit To The Hovel Reverse Note.jpg"
                }
            ],
        "11125452786":
            [
                {
                    "name": "Ned Cassidy Of The Lakes",
                    "file": "PAGE 110 Ned Cassidy Of The Lakes.jpg"
                },
                {
                    "name": "Ned Cassidy Of The Lakes Reverse Note",
                    "file": "PAGE 110 Ned Cassidy Of The Lakes Reverse Note.jpg"
                }
            ],
        "11127076054":
            [
                {
                    "name": "The Lady's Present To Ned",
                    "file": "PAGE 118 The Lady's Present To Ned.jpg"
                },
                {
                    "name": "The Lady's Present To Ned Reverse Note",
                    "file": "PAGE 118 The Lady's Present To Ned Reverse Note.jpg"
                }
            ],
        "11125131876":
            [
                {
                    "name": "Ned Cassidy On The Lakes",
                    "file": "PAGE 126 Ned Cassidy On The Lakes.jpg"
                },
                {
                    "name": "Ned Cassidy On The Lakes Reverse Note",
                    "file": "PAGE 126 Ned Cassidy On The Lakes Reverse Note.jpg"
                }
            ],
        "11127214014":
            [
                {
                    "name": "Ned Saving His Enemy Dan Foley",
                    "file": "PAGE 134 Ned Saving His Enemy Dan Foley.jpg"
                },
                {
                    "name": "Ned Saving His Enemy Dan Foley Reverse Note",
                    "file": "PAGE 134 Ned Saving His Enemy Dan Foley Reverse Note.jpg"
                }
            ],
        "11122097133":
            [
                {
                    "name": "Ned Cassidy Of THe Lakes In 'The Steel Bracelets'",
                    "file": "PAGE 158 Ned Cassidy Of THe Lakes In 'The Steel Bracelets'.jpg"
                },
                {
                    "name": "Ned Cassidy Of THe Lakes In 'The Steel Bracelets' Reverse Note",
                    "file": "PAGE 158 Ned Cassidy Of THe Lakes In 'The Steel Bracelets' Reverse Note.jpg"
                }
            ],
        "11123252635":
            [
                {
                    "name": "Corporal Duffy About To Search The House",
                    "file": "PAGE 166 Corporal Duffy About To Search The House.jpg"
                },
                {
                    "name": "Corporal Duffy About To Search The House Reverse Note",
                    "file": "PAGE 166 Corporal Duffy About To Search The House Reverse Note.jpg"
                }
            ],
        "11120961556":
            [
                {
                    "name": "The Governor Of The Gaol Visits Ned",
                    "file": "PAGE 174 The Governor Of The Gaol Visits Ned.jpg"
                },
                {
                    "name": "The Governor Of The Gaol Visits Ned Reverse Note",
                    "file": "PAGE 174 The Governor Of The Gaol Visits Ned Reverse Note.jpg"
                }
            ]
    }
    for link in to_link:
        images = to_link[link]
        for img in images:
            linked_image = models.LinkedImage()
            linked_image.name = img['name']
            linked_image.file_name = img['file']
            linked_image.location = '/home/spx5ich/linked_images'
            linked_image.image = models.Image.objects.get(flickr_id=link)
            linked_image.description = "This sketch is the property of Tom Gilboy. " \
                                       "Please contact The Illustration Archive for permission to reproduce"

            linked_image.save()


add_irish_life_linked_images()