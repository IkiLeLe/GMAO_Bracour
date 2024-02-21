from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views import generic, View
from .forms import MaintenanceScheduleFilterForm
from django.http import JsonResponse, HttpResponse, FileResponse, Http404, HttpResponseBadRequest
from django.urls import reverse
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import BaseDocTemplate, Table, TableStyle, PageTemplate, Frame, Spacer, Paragraph, Image, PageBreak, LongTable
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from datetime import datetime
from django.utils.encoding import smart_str

import spacy
import csv
import os
from django.conf import settings

from .models import Lines, Equipement, PreventiveTask, CleaningTask, LubrificationTask, Part, Contributor, Contributors
 
# Create your views here.
@method_decorator(login_required, name='dispatch')
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class LineView(generic.TemplateView):
    template_name = 'maintenance_plan/equiplist.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Line_list"] = Lines.objects.all()
        context["Equipement_list"] = Equipement.objects.all()
        return context
    # Dans views.py
@method_decorator(login_required, name='dispatch')
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
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
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class TaskDetailView(generic.DetailView):
    template_name = 'maintenance_plan/taskdetail.html'

    def get_object(self, queryset=None):
        task_type = self.kwargs['task_type']
        task_id = self.kwargs['task_id']

        if task_type == 'preventive':
            task = get_object_or_404(PreventiveTask, id=task_id)
        elif task_type == 'cleaning':
            task = get_object_or_404(CleaningTask, id=task_id)
        elif task_type == 'lubrification':
            task = get_object_or_404(LubrificationTask, id=task_id)
        else:
            # Ajoutez une gestion d'erreur appropriée ici
            task = None  # Ou une autre valeur par défaut

        return task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_type'] = self.kwargs['task_type']
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
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
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
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class ExportCSVView(generic.View):
    def get(self, request, *args, **kwargs):
        tasks = get_filtered_tasks(request)

        active_tab = request.GET.get('active_tab', None)

        if active_tab == 'nav-preventivetask':
            tasks = tasks['preventive_tasks']
            header = ['Equipement', 'Partie', 'Opération', 'Mode', 'Fréquence', 'Element de Construstion','Position', 'Critère', 'Description', 'Niveau', 'Durée', 'Intervenant', 'Référence']
        elif active_tab == 'nav-cleaningtask':
            tasks = tasks['cleaning_tasks']
            header = ['Equipement', 'Partie', 'Opération', 'Mode', 'Fréquence', 'Element de Construstion','Position', 'Aides', 'Description', 'Niveau', 'Durée', 'Intervenant', 'Référence']
        elif active_tab == 'nav-lubrificationtask':
            tasks = tasks['lubrification_tasks']
            header = ['Equipement', 'Partie', 'Opération', 'Mode', 'Fréquence', 'Element de Construstion','Position', 'Lubrification', 'Description', 'Niveau', 'Durée', 'Intervenant', 'Référence']
        else:
            tasks = tasks['preventive_tasks'] + tasks['cleaning_tasks'] + tasks['lubrification_tasks']
            header = ['Operation', 'Equipement', 'Line', 'Criteria', 'Aids', 'Lubrificant', 'Quantity']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="maintenance_schedule.csv"'

        writer = csv.writer(response)

        # Ajout du marqueur BOM pour l'encodage UTF-8
        response.write(u'\ufeff'.encode('utf-8'))
        response.write(','.join(header).encode('utf-8') + b'\n')

        for item in tasks:
            intervenant = ""
            if isinstance(item, PreventiveTask):
                for contributor in item.ison.all():
                    contributors_instances = Contributors.objects.filter(person=contributor, preventive_task=item)
                    total_quantity = sum(instance.quantity for instance in contributors_instances)
                    intervenant += str(total_quantity) + contributor.acronym
                writer.writerow([
                    smart_str(item.part.equipement),
                    smart_str(item.part),
                    smart_str(item.operation),
                    smart_str(item.get_mode_display()),
                    smart_str(item.get_frequency_display()),
                    smart_str(item.component),
                    smart_str(item.location),
                    smart_str(item.criteria),
                    smart_str(item.description),
                    smart_str(item.level),
                    smart_str(item.duration),
                    smart_str(intervenant),
                    smart_str(item.part.document_name)
                ])
            elif isinstance(item, CleaningTask):
                for contributor in item.ison.all():
                    contributors_instances = Contributors.objects.filter(person=contributor, cleaning_task=item)
                    total_quantity = sum(instance.quantity for instance in contributors_instances)
                    intervenant += str(total_quantity) + contributor.acronym
                writer.writerow([
                    smart_str(item.part.equipement),
                    smart_str(item.part),
                    smart_str(item.operation),
                    smart_str(item.get_mode_display()),
                    smart_str(item.get_frequency_display()),
                    smart_str(item.component),
                    smart_str(item.location),
                    smart_str(item.aids),
                    smart_str(item.description),
                    smart_str(item.level),
                    smart_str(item.duration),
                    smart_str(intervenant),
                    smart_str(item.part.document_name)
                ])
            elif isinstance(item, LubrificationTask):
                for contributor in item.ison.all():
                    contributors_instances = Contributors.objects.filter(person=contributor, lubrification_task=item)
                    total_quantity = sum(instance.quantity for instance in contributors_instances)
                    intervenant += str(total_quantity) + contributor.acronym
                writer.writerow([
                    smart_str(item.part.equipement),
                    smart_str(item.part),
                    smart_str(item.operation),
                    smart_str(item.get_mode_display()),
                    smart_str(item.get_frequency_display()),
                    smart_str(item.component),
                    smart_str(item.location),
                    smart_str(item.lubrificant),
                    smart_str(item.description),
                    smart_str(item.level),
                    smart_str(item.duration),
                    smart_str(intervenant),
                    smart_str(item.part.document_name)
                ])

        return response

def split_text(text, max_length=1350):
    """
    Split text into parts with a maximum length without cutting sentences.
    """
    nlp = spacy.load("fr_core_news_sm")
    doc = nlp(text)
    
    result = []
    current_part = ""
    
    for sent in doc.sents:
        if len(current_part) + len(sent.text) <= max_length:
            current_part += sent.text
        else:
            result.append(current_part)
            current_part = sent.text
    if current_part:
        result.append(current_part)
    return result


@method_decorator(login_required, name='dispatch')
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
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
            fontSize=10,
            alignment=4,
        )
        
        times_new_roman_style2 = ParagraphStyle(
            name='TimesNewRoman2',
            parent=getSampleStyleSheet()['Normal'],
            fontName='Times-Roman',  # Spécifiez Times-Roman pour utiliser Times New Roman
            fontSize=10,
            alignment=1,
        )

        # Créez un objet SimpleDocTemplate avec un buffer en tant que toile
        doc = BaseDocTemplate(buffer, pagesize=landscape(letter), leftMargin=30, rightMargin=30, topMargin=80, bottomMargin=20)  
    
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
        content = []
        # Ajouter les données des tâches
        for item in tasks:
            descript = item.description.replace('\n', '<br/>')
            description_parts = split_text(descript)
            for description_part in description_parts:
                data = [item.location, item.operation, item.part.document_name, description_part, ""]
                data_list.append([column_headers, data])
            
                intervenant = ""
            


                if isinstance(item, PreventiveTask):
                    line1 = "Critère: {}".format(item.criteria)
                    for contributor in item.ison.all():
                        contributors_instances = Contributors.objects.filter(person=contributor, preventive_task=item)
                        total_quantity = sum(instance.quantity for instance in contributors_instances)
                        intervenant += str(total_quantity) + contributor.acronym
                elif isinstance(item, CleaningTask):
                    line1 = "Aides: {}".format(item.aids)
                    for contributor in item.ison.all():
                        contributors_instances = Contributors.objects.filter(person=contributor, cleaning_task=item)
                        total_quantity = sum(instance.quantity for instance in contributors_instances)
                        intervenant += str(total_quantity) + contributor.acronym
                elif isinstance(item, LubrificationTask):
                    line1 = "Lubrificant: {}".format(item.lubrificant)
                    for contributor in item.ison.all():
                        contributors_instances = Contributors.objects.filter(person=contributor, lubrification_task=item)
                        total_quantity = sum(instance.quantity for instance in contributors_instances)
                        intervenant += str(total_quantity) + contributor.acronym
                
                line2 = "Outils: {}".format(item.tools)
         
                
                # Ajouter le texte à gauche, au centre et à droite
                left_text = "Machine: {}<br/>Partie: {}<br/>PFE: Safety Gloves, Safety Shoes, Safety Gog, Ear Plug/Ear Muffs, Hairnet (Clean Room)<br/>Le port des EPI est obligatoire<br/>".format(
                    item.part.equipement,
                    item.part.part_name,
                )
                center_text = "ID: {}<br/>{}<br/>Duree: {}<br/>Mode: {}<br/>Frequence: {}".format(
                        item.id,
                        item.part.equipement.lineId,
                        item.duration,
                        item.get_mode_display(),
                        item.get_frequency_display()
                )
                
                
                current_date = datetime.now().strftime("%d %b %y")
                name = ""
                if request.user.position == "Superviseur":
                    name = request.user.get_full_name()

                right_text = "Superviseur: {}<br/>Intervenant: {}".format(
                    name,
                    intervenant)


                # Utiliser Paragraph pour gérer le retour à la ligne automatique
                left_paragraph = Paragraph(left_text, times_new_roman_style)
                center_paragraph = Paragraph(center_text, times_new_roman_style2)
                right_paragraph = Paragraph(right_text, times_new_roman_style)

                # Créer une table à trois colonnes
                text_table_data = [
                    [left_paragraph, center_paragraph, right_paragraph]
                ]
                text_table = Table(text_table_data, colWidths=[doc.width / 3] * 3)
                text_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black)
                ]))
                paragraph1 = Paragraph(line1, times_new_roman_style)
                paragraph2 = Paragraph(line2, times_new_roman_style)
                
                text_line = [paragraph1, paragraph2]
                data_paragraphs = [Paragraph(str(data_item), times_new_roman_style) for data_item in data]
                col_widths = [100, 190, 60, 300, 80]
              

                table = LongTable([column_headers] + [data_paragraphs], colWidths=col_widths)

                # Définir le style de la table
                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('FONTNAME', (0, 0), (-1, 0), 'Times-Roman'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ])  


                table.setStyle(style)
                table._argH[1] = 350
                content.append(text_table)
                content.extend(text_line)
                content.append(Spacer(1, 0.1*inch))
                content.append(table)
                content.append(PageBreak())  

            image_path = item.image.path if item.image else None

            if image_path:
                textimage = "ID: {}<br/>{}<br/>Image {}". format(item.id,item.part.equipement, item.part)
                paragraph = Paragraph(textimage, times_new_roman_style2)
                # Load the image into the PDF document
                image = Image(image_path)
                # Adjust the width and height of the image if needed
                image.drawWidth = 700  # Adjust as per your requirement
                image.drawHeight = 400  # Adjust as per your requirement
                content.append(paragraph)
                content.append(Spacer(1, 0.1*inch))
                content.append(image)
                content.append(PageBreak())  # Add spacer for spacing 
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
            'left_image_path': "static/images/imgcouronne.png",
            'left_image_width': 70,
            'left_image_height': 50,
            'company_name': "BRASSERIE DE LA COURONNE S.A",
            'right_image_path': "static/images/coca-cola.jpg",
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
        left_image.drawOn(self.canvas, self.doc.leftMargin, self.doc.height + self.doc.topMargin - 0.8 * inch)

        # Draw right image
        right_image = Image(right_image_path, width=right_image_width, height=right_image_height)
        right_image.drawOn(self.canvas, self.doc.width - self.doc.rightMargin - 0.3 * inch, self.doc.height + self.doc.topMargin - 0.8 * inch)
        # Définir les styles de police souhaités
        company_name_style = ParagraphStyle(
            name='CompanyName',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=18,
            alignment=1,
            fontName='Times-Roman'  # Utiliser 'Times-Roman' pour Times New Roman
        )

        company_secondary_name_style = ParagraphStyle(
            name='CompanySecondaryName',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=14,
            alignment=1,
            fontName='Courier',
            spaceAfter=6  # Ajuster selon vos besoins
        )
        # Draw company names and other information
        center_text_style = ParagraphStyle(
            name='CenterText',
            parent=getSampleStyleSheet()['Heading1'],
            fontSize=13,
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
        y_position = self.doc.height + self.doc.topMargin - 0.2 * inch
        for element in header_elements:
            element.wrapOn(self.canvas, self.doc.width, self.doc.topMargin)
            element.drawOn(self.canvas, self.doc.leftMargin, y_position)
            y_position -= 0.25 * inch # Adjust spacing if needed


class PartFilterView(View):
    def get(self, request, equipement_serial_number, *args, **kwargs):
        try:
            equipement = get_object_or_404(Equipement, serial_number=equipement_serial_number)
            filtered_parts = Part.objects.filter(equipement=equipement)
            data = [{'value': part.pk, 'text': str(part)} for part in filtered_parts]

            # Ajoutez l'URL en tant que contexte
            data.append({'url': reverse('maintenance_plan:part_filter_view', kwargs={'equipement_serial_number': equipement_serial_number})})

            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
class EquipementFilterView(View):
    def get(self, request, line_id, *args, **kwargs):
        try:
            equipements = Equipement.objects.filter(lineId=line_id)
            data = [{'value': equipement.pk, 'text': str(equipement)} for equipement in equipements]
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)