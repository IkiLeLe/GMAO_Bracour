from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import generic, View
from .forms import MaintenanceScheduleFilterForm
from django.http import JsonResponse, HttpResponse, FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
import reportlab.lib.pagesizes as pagesizes
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import BaseDocTemplate, Table, TableStyle, PageTemplate, Frame, Spacer, Paragraph, Image, PageBreak, LongTable
from reportlab.lib.units import inch
from datetime import datetime

import csv

from .models import Lines, Equipement, PreventiveTask, CleaningTask, LubrificationTask, Part, Contributor, Contributors
 
# Create your views here.
@method_decorator(login_required, name='dispatch')
class LineView(generic.TemplateView):
    template_name = 'maintenance_plan/equiplist.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Line_list"] = Lines.objects.all()
        context["Equipement_list"] = Equipement.objects.all()
        return context
    # Dans views.py
@method_decorator(login_required, name='dispatch')
class EquipementView(generic.DetailView):
    template_name = 'maintenance_plan/equipdetail.html'
    model = Equipement

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipement_instance = self.get_object()
        
        # Get sections related to the equipment
        context['section_data'] = Part.objects.filter(equipement=equipement_instance)
        
        # Get maintenance schedules related to the equipment
        context['preventive_tasks'] = PreventiveTask.objects.filter(part__equipement=equipement_instance)
        context['cleaning_tasks'] = CleaningTask.objects.filter(part__equipement=equipement_instance)
        context['lubrification_tasks'] = LubrificationTask.objects.filter(part__equipement=equipement_instance)
        return context

    
@method_decorator(login_required, name='dispatch')
class MaintenanceScheduleDetailView(generic.DetailView):
    model = PreventiveTask
    template_name = 'maintenance_plan/taskdetail.html'
    context_object_name = 'schedule'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contributors'] = self.object.ison.all()
        return context

def get_filtered_tasks(request):
    form = MaintenanceScheduleFilterForm(request.GET)

    if form.is_valid():
        line_filter = form.cleaned_data.get('line')
        equipement_filter = form.cleaned_data.get('equipement')
        frequency_filter = form.cleaned_data.get('frequency')

        preventive_tasks = PreventiveTask.objects.all()
        cleaning_tasks = CleaningTask.objects.all()
        lubrification_tasks = LubrificationTask.objects.all()

        if line_filter:
            preventive_tasks = preventive_tasks.filter(part__equipement__lineId=line_filter.id)
            cleaning_tasks = cleaning_tasks.filter(part__equipement__lineId=line_filter.id)
            lubrification_tasks = lubrification_tasks.filter(part__equipement__lineId=line_filter.id)

        if equipement_filter:
            preventive_tasks = preventive_tasks.filter(part__equipement=equipement_filter)
            cleaning_tasks = cleaning_tasks.filter(part__equipement=equipement_filter)
            lubrification_tasks = lubrification_tasks.filter(part__equipement=equipement_filter)

        if frequency_filter:
            preventive_tasks = preventive_tasks.filter(frequency__in=frequency_filter)
            cleaning_tasks = cleaning_tasks.filter(frequency__in=frequency_filter)
            lubrification_tasks = lubrification_tasks.filter(frequency__in=frequency_filter)

        tasks = {
            'preventive_tasks': preventive_tasks,
            'cleaning_tasks': cleaning_tasks,
            'lubrification_tasks': lubrification_tasks
        }

        # Ajoutez ces lignes pour le débogage
        print(f'Preventive Tasks: {preventive_tasks.count()}')
        print(f'Cleaning Tasks: {cleaning_tasks.count()}')
        print(f'Lubrification Tasks: {lubrification_tasks.count()}')

        return tasks
    else:
        # Return an empty queryset if the form is not valid
        print(form.errors)
        return {'preventive_tasks': [], 'cleaning_tasks': [], 'lubrification_tasks': []}

@method_decorator(login_required, name='dispatch')
class TaskView(generic.ListView):
    template_name = 'maintenance_plan/task.html'
    context_object_name = 'tasks'
    form_class = MaintenanceScheduleFilterForm

    def get_queryset(self):
        return get_filtered_tasks(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET)
        return context   


@method_decorator(login_required, name='dispatch')
class ExportCSVView(generic.View):
    def get(self, request, *args, **kwargs):
        tasks = get_filtered_tasks(request)

        # Récupérez l'onglet actif à partir des paramètres de requête
        active_tab = request.GET.get('active_tab', None)

        # Filtrez les tâches en fonction de l'onglet actif
        if active_tab == 'nav-preventivetask':
            tasks = tasks['preventive_tasks']
            header = ['Operation', 'Equipement', 'Line', 'Criteria']
        elif active_tab == 'nav-cleaningtask':
            tasks = tasks['cleaning_tasks']
            header = ['Operation', 'Equipement', 'Line', 'Aids']
        elif active_tab == 'nav-lubrificationtask':
            tasks = tasks['lubrification_tasks']
            header = ['Operation', 'Equipement', 'Line', 'Lubrificant', 'Quantity']
        else:
            # Onglet inconnu, utilisez toutes les tâches par défaut
            tasks = tasks['preventive_tasks'] + tasks['cleaning_tasks'] + tasks['lubrification_tasks']
            header = ['Operation', 'Equipement', 'Line', 'Criteria', 'Aids', 'Lubrificant', 'Quantity']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="maintenance_schedule.csv"'

        writer = csv.writer(response)
        writer.writerow(header)

        for item in tasks:
            if isinstance(item, PreventiveTask):
                writer.writerow([item.operation, item.part.equipement.serial_number, item.part.equipement.lineId, item.criteria])
            elif isinstance(item, CleaningTask):
                writer.writerow([item.operation, item.part.equipement.serial_number, item.part.equipement.lineId, item.aids])
            elif isinstance(item, LubrificationTask):
                writer.writerow([item.operation, item.part.equipement.serial_number, item.part.equipement.lineId, item.lubrificant, item.quantity])

        return response

def split_text(text, max_length=1400):
    """
    Split text into parts with a maximum length without cutting words.
    """
    if len(text) > max_length:
        words = text.split()
        result = []
        current_part = ""
        for word in words:
            if len(current_part) + len(word) + 1 <= max_length:
                current_part += word + " "
            else:
                result.append(current_part.rstrip())
                current_part = word + " "
        if current_part:
            result.append(current_part.rstrip())
        return result
    else:
        return [text]



class ExportPDFView(View):
    def get(self, request, *args, **kwargs):

        # Récupérez l'onglet actif à partir des paramètres de requête
        active_tab = request.GET.get('active_tab', None)

        tasks = get_filtered_tasks(request)

        # Filtrez les tâches en fonction de l'onglet actif
        if active_tab == 'nav-preventivetask':
            tasks = tasks['preventive_tasks']
        elif active_tab == 'nav-cleaningtask':
            tasks = tasks['cleaning_tasks']
        elif active_tab == 'nav-lubrificationtask':
            tasks = tasks['lubrification_tasks']
        else:
            # Onglet inconnu, utilisez toutes les tâches par défaut
            tasks = tasks['preventive_tasks'] + tasks['cleaning_tasks'] + tasks['lubrification_tasks']

        # Créez un objet StringIO pour stocker le PDF
        buffer = io.BytesIO()
        styles = getSampleStyleSheet()
        times_new_roman_style = ParagraphStyle(
            name='TimesNewRoman',
            parent=getSampleStyleSheet()['Normal'],
            fontName='Times-Roman',  # Spécifiez Times-Roman pour utiliser Times New Roman
            fontSize=11,
            alignment=0,
        )


        # Créez un objet SimpleDocTemplate avec un buffer en tant que toile
        doc = BaseDocTemplate(buffer, pagesize=landscape(letter))  
    
        page_template = PageTemplate(
            id='header_footer',
            frames=[
                Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='header_frame')
            ],
            onPage=self.header_footer
        )

        doc.addPageTemplates([page_template])

        # Liste pour stocker les données tabulaires
        data_list = []

        # Ajouter les en-têtes de colonne
        column_headers = ["Position", "Opération", "Reférence", "Description", "Remarques"]
        #data_list.append(column_headers)
    
        # Ajouter les données des tâches
        for item in tasks:
            

                # Diviser la description en parties de 50 caractères
            description_parts = split_text(item.description)

                # Ajouter les parties de la description à la liste des données
            for description_part in description_parts:
                data = [item.location, item.operation, item.part.document_name, description_part, ""]
                data_list.append([column_headers, data])

            if isinstance(item, PreventiveTask):
                line1 = "Critère: {}".format(item.criteria)
            elif isinstance(item, CleaningTask):
                line1 = "Aides: {}".format(item.aids)
            elif isinstance(item, LubrificationTask):
                line1 = "Lubrificant: {}".format(item.lubrificant)
            
            line2 = "Outils: {}".format(item.tools)
         
        content = []
       
        for data in data_list:
            
            # Ajouter le texte à gauche, au centre et à droite
            left_text = "Machine: {}<br/>Partie: {}<br/>PFE: Safety Gloves, Safety Shoes, Safety Gog, Ear Plug/Ear Muffs, Hairnet (Clean Room)<br/>Le port des EPI est obligatoire".format(
                item.part.equipement,
                item.part.part_name
            )
            center_text = "{}<br/>Duree: {}<br/>Mode: {}<br/>Debut: <br/>Fin:<br/>Frequence: {}".format(
                    item.part.equipement.lineId,
                    item.duration,
                    item.get_mode_display(),
                    item.get_frequency_display()
            )
            current_date = datetime.now().strftime("%d %b %y")
            right_text = "Date: {}<br/>Superviseur:<br/>Intervenant: <br/>Executeur:".format(
                current_date)


            # Utiliser Paragraph pour gérer le retour à la ligne automatique
            left_paragraph = Paragraph(left_text, times_new_roman_style)
            center_paragraph = Paragraph(center_text, times_new_roman_style)
            right_paragraph = Paragraph(right_text, times_new_roman_style)

            # Créer une table à trois colonnes
            text_table_data = [
                [left_paragraph, center_paragraph, right_paragraph]
            ]
            text_table = Table(text_table_data, colWidths=[doc.width / 3] * 3)
            
            paragraph1 = Paragraph(line1, times_new_roman_style)
            paragraph2 = Paragraph(line2, times_new_roman_style)
            text_lines = [paragraph1, paragraph2]

            data_paragraphs = [Paragraph(str(data_item), times_new_roman_style) for data_item in data[1]]
            col_widths = [100, 200, 50, 300, 80]
            #table_data = data
            

            table = LongTable([column_headers] + [data_paragraphs], colWidths=col_widths)

            # Définir le style de la table
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Times-Roman'),
                #('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                #('LEFTPADDING', (0, 0), (-1, -1), 6),
                #('RIGHTPADDING', (0, 0), (-1, -1), 6),
                #('TOPPADDING', (0, 0), (-1, -1), 3),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                #('ALLOW_WRAP', (0, 0), (-1, -1), True),
                #('WORD_WRAP', (0, 0), (-1, -1), 'CJK'),
                #('SPLITBYROWSPAN', (0, 0), (-1, -1), True),
            ])  # Définir splitByRowSpan à True pour permettre le saut de ligne dans une cellule fusionnée


            table.setStyle(style)
            table._argH[1] = 300
            content.append(Spacer(1, 0.5*inch))
            content.append(text_table)
            content.extend(text_lines)
            content.append(table)
            content.append(PageBreak())   
        # Construisez le document avec 'header_table' suivi de 'table'
        doc.build(content)

         # Réinitialisez le pointeur de lecture du buffer à zéro
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')

        # Créez une réponse FileResponse avec le contenu du buffer PDF
        response['Content-Disposition'] = 'inline; filename="maintenance_schedule.pdf"'

        return response
    
    def header_footer(self, canvas, doc):
        # Header
        self.draw_header(canvas, doc)
        # Footer - You can add footer content if needed

    def draw_header(self, canvas, doc):
        # Get header data
        header_data = {
            'left_image_path': "picture/imgcouronne.png",
            'left_image_width': 70,
            'left_image_height': 50,
            'company_name': "BRASSERIE DE LA COURONNE S.A",
            'right_image_path': "picture/coca-cola.jpg",
            'right_image_width': 90,
            'right_image_height': 50,
            'company_secondary_name': "Coca Cola bottling company of Haïti",
            'document_title': "Preventive Maintenance",
            'document_subtitle': "Work Order"
        }

        # Create a HeaderFrame for the header
        header_frame = HeaderFrame(canvas, doc, header_data=header_data)
        # Draw the header frame
        header_frame.draw()


class HeaderFrame:
    def __init__(self, canvas, doc, **kwargs):
        self.canvas = canvas
        self.doc = doc
        self.header_data = kwargs.pop('header_data', {})

    def draw(self):
        # Draw your header elements here
        left_image_path = self.header_data.get('left_image_path', "")
        left_image_width = self.header_data.get('left_image_width', 0)
        left_image_height = self.header_data.get('left_image_height', 0)

        right_image_path = self.header_data.get('right_image_path', "")
        right_image_width = self.header_data.get('right_image_width', 0)
        right_image_height = self.header_data.get('right_image_height', 0)

        company_name = self.header_data.get('company_name', "")
        company_secondary_name = self.header_data.get('company_secondary_name', "")
        document_title = self.header_data.get('document_title', "")
        document_subtitle = self.header_data.get('document_subtitle', "")

        # Draw left image
        left_image = Image(left_image_path, width=left_image_width, height=left_image_height)
        left_image.drawOn(self.canvas, self.doc.leftMargin, self.doc.height + self.doc.topMargin - 0.25 * inch)

        # Draw right image
        right_image = Image(right_image_path, width=right_image_width, height=right_image_height)
        right_image.drawOn(self.canvas, self.doc.width, self.doc.height + self.doc.topMargin - 0.25 * inch)
        # Définir les styles de police souhaités
        company_name_style = ParagraphStyle(
            name='CompanyName',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=12,
            alignment=1,
            fontName='Times-Roman'  # Utiliser 'Times-Roman' pour Times New Roman
        )

        company_secondary_name_style = ParagraphStyle(
            name='CompanySecondaryName',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=12,
            alignment=1,
            fontName='Courier',
            spaceAfter=6  # Ajuster selon vos besoins
        )
        # Draw company names and other information
        center_text_style = ParagraphStyle(
            name='CenterText',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=12,
            alignment=1,
            fontName='Times-Roman'
        )

        header_elements = [
            Paragraph(company_name, style=company_name_style),
            Paragraph(company_secondary_name, style=company_secondary_name_style),
            Paragraph(document_title, style=center_text_style),
            Paragraph(document_subtitle, style=center_text_style)
        ]

        # Draw header elements on the canvas
        y_position = self.doc.height + self.doc.topMargin + 0.25 * inch
        for element in header_elements:
            element.wrapOn(self.canvas, self.doc.width, self.doc.topMargin)
            element.drawOn(self.canvas, self.doc.leftMargin, y_position - element.height)
            y_position -= element.height/2 # Adjust spacing if needed
    
        

