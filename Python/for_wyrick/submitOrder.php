<?php
include 'configure.inc';

// Load Composer's autoloader (required for PHPMailer)
require 'vendor/autoload.php';
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\SMTP;
use PHPMailer\PHPMailer\Exception;

// Get other information
$vendor = $_POST["vendorPulldown"];
$numItems = $_POST["numItems"];
$budget = $_POST["budget"];
$name = $_POST["name"];

// are we entering a new vendor into the vendor table?
if ($_POST["newVendor"] == "yes")
{
   $insert = "insert into vendors values ("
	."'".$_POST["vendorTextField"]."',"
	."'".$_POST["address1"]."',"
	."'".$_POST["address2"]."',"
	."'".$_POST["address3"]."',"
	."'".$_POST["phone"]."',"
	."'".$_POST["fax"]."',"
	."'".$_POST["webSite"]."')";
   if (!(@ mysqli_query($connection, $insert)))
		die ("Error ".mysql_errno().": ".mysql_error());
		
	$vendor = $_POST["vendorTextField"];
} // /if (new vendor)

// are we editing the vendor table?
if ($_POST["newVendor"] == "edit")
{
   $insert = "update vendors set "
	."vendor='".$_POST["vendorTextField"]."',"
	."address1='".$_POST["address1"]."',"
	."address2='".$_POST["address2"]."',"
	."address3='".$_POST["address3"]."',"
	."phone='".$_POST["phone"]."',"
	."fax='".$_POST["fax"]."',"
	."webSite='".$_POST["webSite"]
	."' where vendor='".$_POST["vendorPulldown"]."'";
   if (!(@ mysqli_query($connection, $insert)))
		die ("Error ".mysql_errno().": ".mysql_error());
		
	$vendor = $_POST["vendorTextField"];
} // /if (new vendor)


$subject = "(for $name) Please order";

// Part of the previous script that used the mail command instead of PHPMailer
// $headers =  "From: $mailFrom\r\n";
// $headers .= "X-Sender: $mailFrom\r\n";
// $headers .= "X-Mailer: PHP\r\n";
// $headers .= "X-Priority: 1\r\n";
// $headers .= "Content-type: text/html\r\n";
// $headers .= "Return-Path: $mailFrom\r\n";

// This was commented out even before we switched over to PHPMailer
//$headers = "Content-Type: text/html; charset=utf-8 \n";
$out = "<HTML><PRE>Hi";
if( $greetName == '' )
{
        $out .= ",\n";

}
else
{
        $out .= " $greetName,\n";
}
$out.= "\n";
$out.= "I would like to order the following items from $vendor:\n";

// collect items from environment
$out.= "\n";
// two tables are created here: one for the email message, the other for database entry
$emailTable = array();
$dbTable = array();
$emailTable[]= array("Catalog#","Description","# of units","Unit","Unit price","Amount");
for($i = 0; $i < $numItems; $i++)
{
   $emailTable[] = array($_POST["catNum_".$i],$_POST["description_".$i],$_POST["numUnits_".$i],$_POST["unit_".$i],sprintf("$%-.2f",$_POST["price_".$i]),sprintf("$%-.2f",$_POST["price_".$i] * $_POST["numUnits_".$i]));
   $dbTable[] = array($_POST["catNum_".$i],$_POST["description_".$i],$_POST["numUnits_".$i],$_POST["unit_".$i],$_POST["price_".$i]);
}

// compute the width of each column
$width = array(0,0,0,0,0,0);
foreach($emailTable as $line)
{
	for ($i = 0; $i < 6; $i++)
	{	
		if (strlen($line[$i]) > $width[$i])
   	{
   	   $width[$i] = strlen($line[$i]);
   	} // /if
   } // /for ($i)
} // /foreach ($table)

// now translate to columns
$column = array(0,0,0,0,0,0);
$linelen = 0;
for ($i = 0; $i < 6; $i++)
{
   $column[$i] = $linelen;
   $linelen += $width[$i] + 3;
} // /for($i)

// now use this information to create the actual text block
foreach ($emailTable as $temp)
{
   $line = str_pad(" ",$linelen);
   for ($i = 0; $i < 6; $i++)
	{
	  $line = substr_replace($line, $temp[$i],$column[$i], 0);
	} // /for ($i)
   $out .= $line."\n";
} // /for ($j)
$out .= "\n";

// Get vendor information
if(!($result = mysqli_query($connection, "select * from vendors where vendor='".$vendor."'")))
{
   showerror();
}
$item = mysqli_fetch_array($result);

$out.=$item[0]."\n";
$out.=$item[1]."\n";
$out.=$item[2]."\n";
if($item[3] != "")
{
   $out.=$item[3]."\n";
}
$out.="phone: ".$item[4]."\n";
$out.="fax: ".$item[5]."\n";
$out.=$item[6]."\n\n";

// Get budget description
if(!($result = mysqli_query($connection, "select description from budgets where ID='".$budget."'")))
{
   showerror();
}
$item = mysqli_fetch_array($result);

$out.= "Please use funds from ".$item[0]." ($budget).\n\n";
$out.="$closing\n\n";
$out.="$signature\n</pre></html>\n";

// Previous command:
// mail( $mailTo, $subject, $out, $headers);

// New command:
$mail = new PHPMailer(true);

//Server settings
$mail->SMTPDebug = SMTP::DEBUG_SERVER;                      // Enable verbose debug output
$mail->isSMTP();                                            // Send using SMTP
$mail->Host       = 'smtp.gmail.com';                       // Set the SMTP server to send through
$mail->SMTPAuth   = true;                                   // Enable SMTP authentication
$mail->Username   = 'wyricklabmailbot@gmail.com';           // SMTP username
$mail->Password   = 'pleaseDon\'tHack';                     // SMTP password
$mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;         // Enable TLS encryption; `PHPMailer::ENCRYPTION_SMTPS` also accepted
$mail->Port       = 587;                                    // TCP port to connect to

//Recipients
$mail->setFrom('wyricklabmailbot@gmail.com', 'Mailer');
$mail->addAddress($mailTo);

// Content
$mail->isHTML(true);
$mail->Subject = $subject;
$mail->Body    = $out;

// Send it!
$mail->send();

mysqli_query($connection, 'select get_lock("submitOrder.php", 20)'); // to avoid race condition
$insert = "insert into event values (NULL, '".$vendor."', NOW(), '".$budget."', '".$name."')";
mysqli_query($connection, $insert);
$query = "select last_insert_id() from event";
$result = mysqli_query($connection, $query);
$row = mysqli_fetch_array($result);
$lastId = $row[0];
mysqli_query($connection, 'select release_lock("submitOrder.php")');

for ($i = 0; $i < $numItems; $i++)
{
   $insert = "insert into item values ($lastId, NULL, "
	."'".$dbTable[$i][0]."', "
	."'".$dbTable[$i][1]."', "
	."'".$dbTable[$i][2]."', "
	."'".$dbTable[$i][3]."', "
	."'".$dbTable[$i][4]."')";

   if (!(@ mysqli_query($connection, $insert)))
		die("Error ".mysql_errno().": ".mysql_error());
} // /for($i)

header("Location: finishedOrder.html");
exit;
