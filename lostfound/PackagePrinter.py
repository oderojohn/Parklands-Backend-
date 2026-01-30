import socket
from datetime import datetime
from escpos.printer import Network
import time
import re

class PackagePrinter:
    """Handles printing of package receipts using ESC/POS commands"""

    def __init__(self, ip="192.168.10.175", port=9100, max_retries=3, retry_delay=2):
        self.PRINTER_IP = ip
        self.PRINTER_PORT = port
        self.MAX_RETRIES = max_retries
        self.RETRY_DELAY = retry_delay
        self.bw_image_path = r"C:\ReceptionIQ\python Backend\myproject\myapp\logo-dark.bmp"

        # ESC/POS commands
        self.ESC = b'\x1b'
        self.GS = b'\x1d'
        self.BOLD_ON = self.ESC + b'\x45\x01'
        self.BOLD_OFF = self.ESC + b'\x45\x00'
        self.QUAD_SIZE_ON = self.GS + b'\x21\x33'
        self.NORMAL_SIZE = self.GS + b'\x21\x00'
        self.CENTER_ALIGN = self.ESC + b'\x61\x01'
        self.LEFT_ALIGN = self.ESC + b'\x61\x00'
        self.LINE_FEED = b'\n'
        self.CUT = self.GS + b'V\x00'

        # Predefined size commands
        self.zes = [
            ('1x1', b'\x1D\x21\x00'),
            ('2x1', b'\x1D\x21\x10'),
            ('1x2', b'\x1D\x21\x01'),
            ('2x2', b'\x1D\x21\x11'),
            ('3x3', b'\x1D\x21\x22')
        ]

    def _mask_phone(self, phone):
        """Mask phone numbers to show first 4 and last 2 digits (0792******01)"""
        if not phone:
            return ""

        # Remove any non-digit characters
        digits = re.sub(r'\D', '', phone)

        if len(digits) >= 6:
            return f"{digits[:4]}******{digits[-2:]}"
        return phone  # Return original if too short to mask

    def _get_printer(self):
        """Establish connection to printer with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                printer = Network(self.PRINTER_IP, self.PRINTER_PORT)
                return printer
            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise
                print(f"Connection attempt {attempt + 1} failed: {str(e)} - retrying...")
                time.sleep(self.RETRY_DELAY)
        return None

    def _set_size(self, printer, size_name):
        """Set text size using predefined zes commands"""
        for name, cmd in self.zes:
            if name == size_name:
                printer._raw(cmd)
                return
        printer._raw(self.zes[0][1])  # Default to 1x1 if not found

    def _print_common_header(self, printer, title, code):
        """Print common header for both receipt types"""
        try:
            printer.image(self.bw_image_path)
        except Exception as img_error:
            print(f"Couldn't print image: {img_error}")

        # Set larger size for code
        self._set_size(printer, '2x2')
        printer.set(align='center', bold=True)
        printer.text(f"{code}\n")
        self._set_size(printer, '1x1')  # Reset size

        printer.set(align='left', bold=False)
        printer.text("\n------------------------------------------\n")
    
    def print_found_receipt(self, found_item):
        if found_item.type.lower() == "card":
            return False

        printer = None
        try:
            printer = self._get_printer()
            if not printer:
                return False

            # Print logo at the top
            try:
                printer.image(self.bw_image_path)
            except Exception as img_error:
                print(f"Couldn't print image: {img_error}")

            printer.set(align='center', bold=True)
            printer.text("PARKLANDS SPORTS CLUB\n")
            printer.set(bold=False)
            printer.text("PO BOX 123-456, NAIROBI\n")
            printer.text("Tel: 0712 345 6789\n")
            printer.text("Web: www.parklandssportsclub.org\n")
            printer.text("\n")

            printer.set(bold=True)
            printer.text("FOUND ITEM RECEIPT\n")
            printer.set(bold=False)
            printer.text("\n")

            # Large item ID
            self._set_size(printer, '2x2')
            printer.set(align='center', bold=True)
            printer.text(f"{found_item.id}\n")
            self._set_size(printer, '1x1')  # Reset size
            printer.set(bold=False)
            printer.text("\n")

            printer.set(align='left', bold=True)
            printer.text("Item Details\n")
            printer.set(bold=False)
            printer.text("-----------------------------\n")
            printer.set(bold=True)
            printer.text(f"Type: {found_item.type}\n")
            printer.set(bold=False)
            printer.text(f"Description: {found_item.description}\n")
            printer.text(f"Place Found: {found_item.place_found}\n")

            printer.text("\n")
            printer.set(bold=True)
            printer.text("Finder Information\n")
            printer.set(bold=False)
            printer.text("-----------------------------\n")
            printer.set(bold=True)
            printer.text(f"Name: {found_item.finder_name}\n")
            printer.set(bold=False)
            printer.text(f"Phone: {found_item.finder_phone}\n")

            printer.text("\n")
            printer.set(bold=True)
            printer.text(f"Date Reported: {found_item.date_reported.strftime('%Y-%m-%d %H:%M')}\n")
            printer.set(bold=False)
            printer.text(f"Status: {found_item.status}\n")

            qr_data = str(found_item.id)
            printer._raw(b"\n" + self.CENTER_ALIGN)

            store_len = len(qr_data) + 3
            pL = store_len % 256
            pH = store_len // 256
            printer._raw(self.GS + b'(k' + bytes([pL, pH]) + b'\x31\x50\x30' + qr_data.encode('utf-8'))
            printer._raw(self.GS + b'(k\x03\x00\x31\x41\x32')
            printer._raw(self.GS + b'(k\x03\x00\x31\x43\x06')
            printer._raw(self.GS + b'(k\x03\x00\x31\x45\x30')
            printer._raw(self.GS + b'(k\x03\x00\x31\x51\x30')

            printer._raw(b"\n" * 2 + self.CENTER_ALIGN + self.BOLD_ON)
            printer._raw(b"Thank you for using PSC Lost+Found\n")
            printer._raw(b"Handled by PSC ICT Department\n")
            printer._raw(self.BOLD_OFF + b"\n")

            printer._raw(b"\n" * 3)
            printer._raw(self.CUT)

            return True
        
        except Exception as e:
            print(f"Printing failed: {str(e)}")
            return False
        
    def print_match_receipts(self, matches):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as printer:
                printer.connect((self.PRINTER_IP, self.PRINTER_PORT))

                printer.sendall(self.CENTER_ALIGN + self.BOLD_ON)
                printer.sendall(b"PARKLANDS SPORTS CLUB - LOST+FOUND\n")
                printer.sendall(self.BOLD_OFF + b"\n")

                for i, match_data in enumerate(matches, start=1):
                    lost = match_data['lost_item']
                    found = match_data['found_item']

                    printer.sendall(self.CENTER_ALIGN + self.BOLD_ON)
                    printer.sendall(f"MATCH #{i}\n".encode('utf-8'))
                    printer.sendall(self.BOLD_OFF)

                    printer.sendall(self.LEFT_ALIGN + b"Lost Item: " + str(lost['item_name']).encode() + b"\n")
                    printer.sendall(b"Desc: " + str(lost['description']).encode() + b"\n")
                    printer.sendall(b"Lost at: " + str(lost['place_lost']).encode() + b"\n")
                    printer.sendall(b"Reporter: " + str(lost.get('reporter_email', '')).encode() + b"\n\n")

                    printer.sendall(self.LEFT_ALIGN + b"Found Item: " + str(found['item_name']).encode() + b"\n")
                    printer.sendall(b"Desc: " + str(found['description']).encode() + b"\n")
                    printer.sendall(b"Found at: " + str(found['place_found']).encode() + b"\n")
                    printer.sendall(b"Finder: " + str(found.get('finder_name', '')).encode() + b"\n")
                    printer.sendall(b"-" * 32 + b"\n\n")  # separator between matches

                # Footer + cut once at the end
                printer.sendall(self.CENTER_ALIGN + self.BOLD_ON)
                printer.sendall(b"\nEnd of Match Report\n")
                printer.sendall(b"PSC ICT Department\n")
                printer.sendall(self.BOLD_OFF + b"\n")

                printer.sendall(b"\n" * 4)
                printer.sendall(self.CUT)

            return True

        except Exception as e:
            print(f"Printing failed: {e}")
            return False

    def print_lost_receipt(self, lost_item):
        if lost_item.type.lower() == "card":
            return False

        printer = None
        try:
            printer = self._get_printer()
            if not printer:
                return False

            # Print logo at the top
            try:
                printer.image(self.bw_image_path)
            except Exception as img_error:
                print(f"Couldn't print image: {img_error}")

            printer.set(align='center', bold=True)
            printer.text("PARKLANDS SPORTS CLUB\n")
            printer.set(bold=False)
            printer.text("PO BOX 123-456, NAIROBI\n")
            printer.text("Tel: 0712 345 6789\n")
            printer.text("Web: www.parklandssportsclub.org\n")
            printer.text("\n")

            printer.set(bold=True)
            printer.text("LOST ITEM REPORT RECEIPT\n")
            printer.set(bold=False)
            printer.text("\n")

            # Large tracking ID
            self._set_size(printer, '2x2')
            printer.set(align='center', bold=True)
            printer.text(f"{lost_item.tracking_id}\n")
            self._set_size(printer, '1x1')  # Reset size
            printer.set(bold=False)
            printer.text("\n")

            printer.set(align='left', bold=True)
            printer.text("Item Details\n")
            printer.set(bold=False)
            printer.text("-----------------------------\n")
            printer.set(bold=True)
            printer.text(f"Type: {lost_item.type}\n")
            printer.set(bold=False)
            if lost_item.item_name:
                printer.text(f"Item Name: {lost_item.item_name}\n")
            if lost_item.card_last_four:
                printer.text(f"Card Last Four: {lost_item.card_last_four}\n")
            printer.text(f"Description: {lost_item.description or ''}\n")
            printer.text(f"Place Lost: {lost_item.place_lost or ''}\n")

            printer.text("\n")
            printer.set(bold=True)
            printer.text("Reporter Information\n")
            printer.set(bold=False)
            printer.text("-----------------------------\n")
            printer.set(bold=True)
            printer.text(f"Name: {lost_item.owner_name or ''}\n")
            printer.set(bold=False)
            if lost_item.reporter_phone:
                printer.text(f"Phone: {lost_item.reporter_phone}\n")
            if lost_item.reporter_email:
                printer.text(f"Email: {lost_item.reporter_email}\n")

            printer.text("\n")
            printer.set(bold=True)
            printer.text(f"Date Reported: {lost_item.date_reported.strftime('%Y-%m-%d %H:%M')}\n")
            printer.set(bold=False)
            printer.text(f"Status: {lost_item.status}\n")

            qr_data = str(lost_item.tracking_id)
            printer._raw(b"\n" + self.CENTER_ALIGN)

            store_len = len(qr_data) + 3
            pL = store_len % 256
            pH = store_len // 256
            printer._raw(self.GS + b'(k' + bytes([pL, pH]) + b'\x31\x50\x30' + qr_data.encode('utf-8'))
            printer._raw(self.GS + b'(k\x03\x00\x31\x41\x32')
            printer._raw(self.GS + b'(k\x03\x00\x31\x43\x06')
            printer._raw(self.GS + b'(k\x03\x00\x31\x45\x30')
            printer._raw(self.GS + b'(k\x03\x00\x31\x51\x30')

            printer._raw(b"\n" * 2 + self.CENTER_ALIGN + self.BOLD_ON)
            printer._raw(b"Thank you for reporting your lost item\n")
            printer._raw(b"Handled by PSC ICT Department\n")
            printer._raw(self.BOLD_OFF + b"\n")

            printer._raw(b"\n" * 3)
            printer._raw(self.CUT)

            return True

        except Exception as e:
            print(f"Printing failed: {str(e)}")
            return False
