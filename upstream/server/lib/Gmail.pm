#
# Licensed to the Apache Software Foundation (ASF) under one or or more
# contributor license agreements. See the NOTICE file distributed with this
# work for additional information regarding copyright ownership. The ASF
# licenses this file to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

package Plugins::Gmail;
use Mojo::Base 'Mojolicious::Plugin';

use File::Basename qw(basename);
use File::Spec qw(basename);
use MIME::Base64;
use Mojo::Util qw(dumper slurp trim);
use Net::SMTPS;
use Net::SMTP;
use Time::Piece;

use constant {
  DEBUG          => $ENV{MOJO_GMAIL_DEBUG}          // 0,
  NO_AUTOCONNECT => $ENV{MOJO_GMAIL_NO_AUTOCONNECT} // 0
};

our $VERSION = '1.0';

has conf  => sub { +{} };
has 'error';
has 'sender';

sub register {
  my ($plugin, $app, $conf) = @_;

  # need login and pass
  die 'No login provided.' unless $conf->{login};
  die 'No pass provided.'  unless $conf->{pass};

  # default values
  $conf->{connected}          = 0;
  $conf->{smtp}             //= 'smtp.gmail.com';
  $conf->{layer}            //= 'tls'; # ssl/tls, starttls, none
  $conf->{auth}             //= 'LOGIN';
  $conf->{from}             //= $conf->{login};
  $conf->{timeout}          //= 60;
  $conf->{ssl_verify_mode}  //= '';
  $conf->{ssl_ca_file}      //= '';
  $conf->{ssl_ca_path}      //= '';

  # set port if default
  unless ($conf->{port}) {
    $conf->{port} = 25;
    $conf->{port} = 465 if ($conf->{layer} eq 'ssl');
    $conf->{port} = 587 if ($conf->{layer} eq 'starttls');
  }

  # save config
  $plugin->conf($conf) if $conf;

  # ensure sane defaults
  $plugin->_connect unless NO_AUTOCONNECT;

  $app->helper('gmail.send' => sub {
    my $self = shift;
    my %args = @_; # rest of params by hash

    # connect unless alread are
    unless ($self->{sender} || $plugin->_connect) {
      my $error = 'Unable to connect to remote server.';
      warn $error if DEBUG;
      $plugin->error($error);
      return undef;
    }

    my $verbose = $args{'verbose'} // 0;

    # load all the email param
    my $mail = {};

    $mail->{to} = $args{'to'} // '';

    if ($mail->{to} eq '') {
      my $error = 'No RCPT found. Please add the TO field.';
      warn $error if DEBUG;
      $plugin->error($error);
      return undef;
    }

    $mail->{from}    = $args{'from'}      // $self->{from};
    $mail->{replyto} = $args{'replyto'}   // $mail->{from};
    $mail->{cc}      = $args{'cc'}        // '';
    $mail->{bcc}     = $args{'bcc'}       // '';
    $mail->{charset} = $args{'charset'}   // 'UTF-8';

    $mail->{type}    = $args{'type'}      // 'text/plain';
    $mail->{subject} = $args{'subject'}   // '';
    $mail->{body}    = $args{'body'}      // '';

    $mail->{attachments} = $plugin->_check_attachments($args{'attachments'} // []);

    my $boundary = 'gmail-boundary-' . gmtime->epoch;

    my $sender = $plugin->sender;

    $sender->mail($mail->{from} . "\n");

    # add all our recipients to the list
    for my $recipients ( ($mail->{to}, $mail->{cc}, $mail->{bcc}) ) {
      unless ($sender->recipient(split(/;/, $recipients))) {
        $plugin->error($sender->message);
        $sender->reset;
        $sender->quit;
      }
    }

    $sender->data;

    # send header
    $sender->datasend("From: " . $mail->{from} . "\n");
    $sender->datasend("To: " . $mail->{to} . "\n");
    $sender->datasend("Cc: " . $mail->{cc} . "\n") if ($mail->{cc} ne '');
    $sender->datasend("Reply-To: " . $mail->{replyto} . "\n");
    $sender->datasend("Subject: " . $mail->{subject} . "\n");
    $sender->datasend("Date: " . localtime->strftime("%a, %d %b %Y %T %z"). "\n");

    # check for attachments
    if (scalar @{$mail->{attachments}}) {
      print "With Attachments\n" if $verbose;
      $sender->datasend("MIME-Version: 1.0\n");
      $sender->datasend("Content-Type: multipart/mixed; BOUNDARY=\"$boundary\"\n");

      # Send text body
      $sender->datasend("\n--$boundary\n");
      $sender->datasend("Content-Type: ".$mail->{type}."; charset=".$mail->{charset}."\n");

      $sender->datasend("\n");
      $sender->datasend($mail->{body} . "\n\n");

      my $attachments=$mail->{attachmentlist};
      foreach my $file (@$attachments) {
        my($bytesread, $buffer, $data, $total);

        $file=~s/\A[\s,\0,\t,\n,\r]*//;
        $file=~s/[\s,\0,\t,\n,\r]*\Z//;

        my $opened=open(my $f,'<',$file);
        binmode($file);
        while (($bytesread = sysread($f, $buffer, 1024)) == 1024) {
          $total += $bytesread;
          $data .= $buffer;
        }
        if ($bytesread) {
          $data .= $buffer;
          $total += $bytesread;
        }
        close $f;
        # Get the file name without its directory
        my $filename = basename($file);
        # Get the MIME type
        my $type = 'meh'; #guess_media_type($file);
        say "Composing MIME with attach $file\n" if DEBUG;
        if ($data) {
          $sender->datasend("--$boundary\n");
          $sender->datasend("Content-Type: $type; name=\"$filename\"\n");
          $sender->datasend("Content-Transfer-Encoding: base64\n");
          $sender->datasend("Content-Disposition: attachment; =filename=\"$filename\"\n\n");
          $sender->datasend(encode_base64($data));
          $sender->datasend("--$boundary\n");
        }
      }

      $sender->datasend("\n--$boundary--\n"); # send endboundary end message
    }

    # no attachments
    else {
      # send text body
      $sender->datasend("MIME-Version: 1.0\n");
      $sender->datasend("Content-Type: " . $mail->{type}. "; charset=" . $mail->{charset} . "\n");

      $sender->datasend("\n");
      $sender->datasend($mail->{body}."\n\n");
    }

    $sender->datasend("\n");

    my $ret = 1;

    unless ($sender->dataend) {
      my $error = $sender->message;
      warn $error if DEBUG;
      $plugin->error($error);
      $ret = 0;
    }

    $sender->quit;
    return $ret;
  });
}

sub _connect {
  my $self = shift;

  my $conf = $self->conf;

  # The module sets the SMTP google but could use another!
  printf("Connecting to %s using %s with %s and timeout of %s\n", $conf->{smtp}, $conf->{layer}, $conf->{auth}, $conf->{timeout}) if DEBUG;

  my $l = $conf->{layer};

  my $sender;

  # Set security layer from $layer
  if (!defined($l) || $l eq 'none') {
    $sender = Net::SMTP->new(
      $conf->{smtp},
      Debug   => DEBUG,
      Port    => $conf->{port},
      Timeout => $conf->{timeout}
    );
  }
  else {
    $sender = Net::SMTPS->new(
      $conf->{smtp},
      Debug           => DEBUG,
      doSSL           => ($l eq 'tls') ? 'starttls' : ($l eq 'ssl') ? 'ssl' : undef,
      Port            => $conf->{port},
      SSL_ca_file     => $conf->{ssl_ca_file},
      SSL_ca_path     => $conf->{ssl_ca_path},
      SSL_verify_mode => $conf->{ssl_verify_mode},
      Timeout         => $conf->{timeout},
    );
  }

  my $error;

  unless ($sender) {
    $error = sprintf "Could not connect to SMTP server (%s:%s)", $conf->{smtp}, $conf->{port};
    warn $error if DEBUG;
    return 0;
  }

  unless($conf->{auth} eq 'none') {
    $error = $sender->message unless $sender->auth($conf->{login}, $conf->{pass}, $conf->{auth});
    return 0;
  }

  # store any errors
  $self->error($error);
  $self->sender($sender);

  return !!$sender;
}

sub _check_attachments {
# Checks that all the attachments exist
  my $self = shift;
  my $attachments = shift;

  my $result = [];

  foreach my $file (@$attachments) {
    $file =~ s/\A[\s,\0,\t,\n,\r]*//;
    $file =~ s/[\s,\0,\t,\n,\r]*\Z//;

    unless (-f $file ) {
      print "Unable to find the attachment file: $file (removed from list)\n" if DEBUG;
    }
    else {
      if ( open(my $f, '<', $file) ) {
        push @{$result}, $file;
        close $f;
        print "Attachment file: $file added\n" if DEBUG;
      }
      else {
        print "Unable to open the attachment file: $file (removed from list)\n" if DEBUG;
      }
    }
  }

  return $result;
}

1;

